from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import Control, Domain, Framework, Scale, User
from ..schemas import FrameworkDetail, FrameworkOut
from ..security import get_current_user

router = APIRouter(prefix="/api/frameworks", tags=["frameworks"])


@router.get("", response_model=list[FrameworkOut])
def list_frameworks(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return list(db.scalars(select(Framework).order_by(Framework.name)))


@router.get("/{framework_id}", response_model=FrameworkDetail)
def get_framework(framework_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    framework = db.scalar(
        select(Framework)
        .where(Framework.id == framework_id)
        .options(
            selectinload(Framework.domains)
            .selectinload(Domain.controls)
            .selectinload(Control.questions),
            selectinload(Framework.domains)
            .selectinload(Domain.scale)
            .selectinload(Scale.options),
        )
    )
    if not framework:
        raise HTTPException(404, "Framework não encontrado")
    return framework
