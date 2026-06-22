"""Seeding / re-seeding: ParsedFramework -> database (idempotent upsert)."""
from __future__ import annotations

import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import (
    Control,
    Domain,
    Framework,
    Question,
    Scale,
    ScaleOption,
    User,
)
from ..security import hash_password
from .base import ParsedFramework
from .viaconnect_parser import ViaconnectParser


def _upsert_scale(db: Session, parsed) -> Scale:
    scale = db.scalar(select(Scale).where(Scale.key == parsed.key))
    if scale is None:
        scale = Scale(key=parsed.key)
        db.add(scale)
    scale.name = parsed.name
    scale.min_value = parsed.min_value
    scale.max_value = parsed.max_value
    db.flush()

    # Read persisted options from the DB (not the relationship cache), so that
    # shared scales already populated in this same session are detected.
    existing = {
        o.value: o
        for o in db.scalars(select(ScaleOption).where(ScaleOption.scale_id == scale.id))
    }
    for opt in parsed.options:
        row = existing.get(opt.value)
        if row is None:
            db.add(ScaleOption(scale_id=scale.id, value=opt.value, label=opt.label))
        else:
            row.label = opt.label
    db.flush()
    return scale


def seed_framework(db: Session, parsed: ParsedFramework) -> dict:
    """Upsert a parsed framework. Returns a small summary for the API/logs."""
    framework = db.scalar(select(Framework).where(Framework.slug == parsed.slug))
    if framework is None:
        framework = Framework(slug=parsed.slug)
        db.add(framework)
    framework.name = parsed.name
    framework.description = parsed.description
    framework.source_file = parsed.source_file
    db.flush()

    n_domains = n_controls = n_questions = 0
    for d_idx, pd in enumerate(parsed.domains):
        scale = _upsert_scale(db, pd.scale)

        domain = db.scalar(
            select(Domain).where(Domain.framework_id == framework.id, Domain.key == pd.key)
        )
        if domain is None:
            domain = Domain(framework_id=framework.id, key=pd.key)
            db.add(domain)
        domain.scale_id = scale.id
        domain.name = pd.name
        domain.reference_model = pd.reference_model
        domain.maintainer = pd.maintainer
        domain.scale_text = pd.scale_text
        domain.reference_url = pd.reference_url
        domain.order_index = d_idx
        db.flush()
        n_domains += 1

        for c_idx, pc in enumerate(pd.controls):
            control = db.scalar(
                select(Control).where(Control.domain_id == domain.id, Control.code == pc.code)
            )
            if control is None:
                control = Control(domain_id=domain.id, code=pc.code)
                db.add(control)
            control.name = pc.name
            control.order_index = c_idx
            db.flush()
            n_controls += 1

            for q_idx, pq in enumerate(pc.questions):
                question = db.scalar(select(Question).where(Question.code == pq.code))
                if question is None:
                    question = Question(code=pq.code)
                    db.add(question)
                question.control_id = control.id
                question.text = pq.text
                question.guidance = pq.guidance
                question.weight = pq.weight
                question.order_index = q_idx
                db.flush()
                n_questions += 1

    db.commit()
    return {
        "framework": framework.slug,
        "domains": n_domains,
        "controls": n_controls,
        "questions": n_questions,
    }


def seed_admin(db: Session) -> None:
    """Create the seed admin from .env if no users exist yet."""
    if db.scalar(select(User).where(User.username == settings.admin_username)):
        return
    db.add(
        User(
            username=settings.admin_username,
            full_name=settings.admin_full_name,
            hashed_password=hash_password(settings.admin_password),
            is_active=True,
            is_admin=True,
        )
    )
    db.commit()


def workbook_path() -> str:
    return os.path.join(settings.frameworks_dir, settings.seed_workbook)


def run_seed(db: Session, path: str | None = None) -> dict:
    """Parse the configured workbook and seed/re-seed the catalog + admin."""
    path = path or workbook_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Workbook not found: {path}")
    parsed = ViaconnectParser().parse(path)
    summary = seed_framework(db, parsed)
    seed_admin(db)
    summary["source"] = path
    return summary
