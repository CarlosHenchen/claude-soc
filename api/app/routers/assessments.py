from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Assessment, Framework, Question, Response as ResponseModel, User
from ..schemas import (
    AssessmentCreate,
    AssessmentDetail,
    AssessmentOut,
    AssessmentUpdate,
    DashboardOut,
    ResponseInput,
    ResponseOut,
)
from ..security import get_current_user
from ..services.report import build_report_html
from ..services.scoring import compute_dashboard, persist_scores

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


def _get_or_404(db: Session, assessment_id: int) -> Assessment:
    a = db.get(Assessment, assessment_id)
    if not a:
        raise HTTPException(404, "Avaliação não encontrada")
    return a


@router.get("", response_model=list[AssessmentOut])
def list_assessments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return list(db.scalars(select(Assessment).order_by(Assessment.created_at.desc())))


@router.post("", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not db.get(Framework, payload.framework_id):
        raise HTTPException(400, "Framework inválido")
    a = Assessment(
        framework_id=payload.framework_id,
        name=payload.name,
        client=payload.client,
        assessor=payload.assessor,
        notes=payload.notes,
        created_by_id=current.id,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.get("/{assessment_id}", response_model=AssessmentDetail)
def get_assessment(assessment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return _get_or_404(db, assessment_id)


@router.patch("/{assessment_id}", response_model=AssessmentOut)
def update_assessment(
    assessment_id: int,
    payload: AssessmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    a = _get_or_404(db, assessment_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(assessment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    a = _get_or_404(db, assessment_id)
    db.delete(a)
    db.commit()


# ---- Responses -----------------------------------------------------------

@router.get("/{assessment_id}/responses", response_model=list[ResponseOut])
def list_responses(assessment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    _get_or_404(db, assessment_id)
    return list(db.scalars(select(ResponseModel).where(ResponseModel.assessment_id == assessment_id)))


@router.put("/{assessment_id}/responses", response_model=list[ResponseOut])
def upsert_responses(
    assessment_id: int,
    payload: list[ResponseInput],
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Bulk upsert of responses. Sends only the changed/answered questions."""
    a = _get_or_404(db, assessment_id)
    existing = {
        r.question_id: r
        for r in db.scalars(select(ResponseModel).where(ResponseModel.assessment_id == assessment_id))
    }
    valid_qids = set(db.scalars(select(Question.id)))
    for item in payload:
        if item.question_id not in valid_qids:
            raise HTTPException(400, f"Pergunta inválida: {item.question_id}")
        r = existing.get(item.question_id)
        if r is None:
            r = ResponseModel(assessment_id=assessment_id, question_id=item.question_id)
            db.add(r)
            existing[item.question_id] = r
        r.current_value = item.current_value
        r.target_value = item.target_value
        r.evidence = item.evidence
    db.commit()
    # Refresh persisted score snapshot after saving responses.
    persist_scores(db, a, compute_dashboard(db, a))
    return list(db.scalars(select(ResponseModel).where(ResponseModel.assessment_id == assessment_id)))


# ---- Dashboard / scores --------------------------------------------------

@router.get("/{assessment_id}/dashboard", response_model=DashboardOut)
def dashboard(assessment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    a = _get_or_404(db, assessment_id)
    return compute_dashboard(db, a)


@router.post("/{assessment_id}/recompute", response_model=DashboardOut)
def recompute(assessment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    a = _get_or_404(db, assessment_id)
    result = compute_dashboard(db, a)
    persist_scores(db, a, result)
    return result


# ---- PDF report (server-side, vector charts via Playwright) ----------------

@router.get("/{assessment_id}/report.pdf")
def report_pdf(assessment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Render the assessment report (cover + exec summary + per-domain) to a
    vector PDF. Charts are ECharts SVG, printed by headless Chromium."""
    a = _get_or_404(db, assessment_id)
    framework = db.get(Framework, a.framework_id)
    dash = compute_dashboard(db, a)
    html = build_report_html(a, framework.name if framework else "", dash)
    try:
        from ..services.pdf import html_to_pdf

        pdf = html_to_pdf(html)
    except Exception as e:  # Playwright/Chromium missing or render failure
        raise HTTPException(
            status_code=503,
            detail=f"Geração de PDF indisponível (Playwright/Chromium): {e}",
        )
    filename = f"relatorio-{assessment_id}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
