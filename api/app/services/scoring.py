"""Scoring service — reproduces the workbook's consolidation logic.

Per the "Dash" sheet:
  * control (subdomain) maturity = (weighted) mean of its answered items
  * domain  maturity            = (weighted) mean of all its answered items
  * overall maturity            = mean of the domains' NORMALIZED scores

Because each domain uses a different scale (0-3, 0-4, 1-5, 0-5), raw levels are
not comparable across domains. We therefore also report a normalized percentage
(level / scale_max * 100) and use it for the cross-domain radar and the overall
gauge. The same is computed for the target ("Meta") and the gap (target - atual).
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Assessment, Control, Domain, Framework, Response, Score, ScoreScope


def _wmean(pairs: list[tuple[float, float]]) -> float | None:
    """Weighted mean of (value, weight) pairs; None if no data."""
    num = sum(v * w for v, w in pairs)
    den = sum(w for _, w in pairs)
    return (num / den) if den else None


def _pct(raw: float | None, scale_max: int) -> float | None:
    if raw is None or not scale_max:
        return None
    return round(raw / scale_max * 100.0, 2)


def compute_dashboard(db: Session, assessment: Assessment) -> dict:
    """Compute the full live dashboard structure for an assessment."""
    framework = db.scalar(
        select(Framework)
        .where(Framework.id == assessment.framework_id)
        .options(
            selectinload(Framework.domains)
            .selectinload(Domain.controls)
            .selectinload(Control.questions),
            selectinload(Framework.domains).selectinload(Domain.scale),
        )
    )
    # responses keyed by question id
    responses = {
        r.question_id: r
        for r in db.scalars(
            select(Response).where(Response.assessment_id == assessment.id)
        )
    }

    domain_scores: list[dict] = []
    domain_pcts: list[float] = []
    target_pcts: list[float] = []
    grand_answered = grand_total = 0

    for domain in sorted(framework.domains, key=lambda d: d.order_index):
        scale = domain.scale
        smax = scale.max_value
        d_cur: list[tuple[float, float]] = []
        d_tgt: list[tuple[float, float]] = []
        d_answered = d_total = 0
        control_scores: list[dict] = []

        for control in sorted(domain.controls, key=lambda c: c.order_index):
            c_cur: list[tuple[float, float]] = []
            c_tgt: list[tuple[float, float]] = []
            c_answered = c_total = 0
            for q in sorted(control.questions, key=lambda q: q.order_index):
                w = float(q.weight or 1.0)
                c_total += 1
                r = responses.get(q.id)
                if r and r.current_value is not None:
                    c_cur.append((float(r.current_value), w))
                    c_answered += 1
                if r and r.target_value is not None:
                    c_tgt.append((float(r.target_value), w))

            c_raw = _wmean(c_cur)
            c_traw = _wmean(c_tgt)
            control_scores.append(
                {
                    "scope": ScoreScope.control.value,
                    "scope_id": control.id,
                    "label": control.code,
                    "raw_score": round(c_raw, 3) if c_raw is not None else None,
                    "normalized_pct": _pct(c_raw, smax),
                    "target_raw": round(c_traw, 3) if c_traw is not None else None,
                    "target_pct": _pct(c_traw, smax),
                    "gap": round(c_traw - c_raw, 3) if (c_raw is not None and c_traw is not None) else None,
                    "scale_min": scale.min_value,
                    "scale_max": smax,
                    "answered": c_answered,
                    "total": c_total,
                }
            )
            d_cur += c_cur
            d_tgt += c_tgt
            d_answered += c_answered
            d_total += c_total

        d_raw = _wmean(d_cur)
        d_traw = _wmean(d_tgt)
        d_pct = _pct(d_raw, smax)
        d_tpct = _pct(d_traw, smax)
        if d_pct is not None:
            domain_pcts.append(d_pct)
        if d_tpct is not None:
            target_pcts.append(d_tpct)
        grand_answered += d_answered
        grand_total += d_total

        domain_scores.append(
            {
                "scope": ScoreScope.domain.value,
                "scope_id": domain.id,
                "label": domain.key,
                "raw_score": round(d_raw, 3) if d_raw is not None else None,
                "normalized_pct": d_pct,
                "target_raw": round(d_traw, 3) if d_traw is not None else None,
                "target_pct": d_tpct,
                "gap": round(d_traw - d_raw, 3) if (d_raw is not None and d_traw is not None) else None,
                "scale_min": scale.min_value,
                "scale_max": smax,
                "answered": d_answered,
                "total": d_total,
                "controls": control_scores,
            }
        )

    overall_pct = round(sum(domain_pcts) / len(domain_pcts), 2) if domain_pcts else None
    overall_tpct = round(sum(target_pcts) / len(target_pcts), 2) if target_pcts else None
    overall = {
        "scope": ScoreScope.overall.value,
        "scope_id": None,
        "label": "Maturidade geral",
        # Raw is not meaningful across mixed scales; overall is expressed as %.
        "raw_score": None,
        "normalized_pct": overall_pct,
        "target_raw": None,
        "target_pct": overall_tpct,
        "gap": round(overall_tpct - overall_pct, 2) if (overall_pct is not None and overall_tpct is not None) else None,
        "scale_min": 0,
        "scale_max": 100,
        "answered": grand_answered,
        "total": grand_total,
    }

    return {
        "assessment_id": assessment.id,
        "overall": overall,
        "domains": domain_scores,
    }


def persist_scores(db: Session, assessment: Assessment, dashboard: dict) -> None:
    """Replace the persisted Score snapshot for an assessment."""
    db.query(Score).filter(Score.assessment_id == assessment.id).delete()

    def _row(d: dict) -> Score:
        return Score(
            assessment_id=assessment.id,
            scope=ScoreScope(d["scope"]),
            scope_id=d["scope_id"],
            scope_label=d["label"],
            raw_score=d["raw_score"],
            normalized_pct=d["normalized_pct"],
            target_raw=d["target_raw"],
            target_pct=d["target_pct"],
            gap=d["gap"],
            answered=d["answered"],
            total=d["total"],
        )

    db.add(_row(dashboard["overall"]))
    for dom in dashboard["domains"]:
        db.add(_row(dom))
        for ctrl in dom["controls"]:
            db.add(_row(ctrl))
    db.commit()
