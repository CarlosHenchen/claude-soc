from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..ingest import run_seed, workbook_path
from ..models import User
from ..security import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/frameworks-dir")
def list_workbooks(_: User = Depends(require_admin)):
    """List .xlsx files available in the read-only frameworks bind mount."""
    d = settings.frameworks_dir
    files = []
    if os.path.isdir(d):
        files = sorted(f for f in os.listdir(d) if f.lower().endswith(".xlsx"))
    return {"dir": d, "current": settings.seed_workbook, "files": files}


@router.post("/reseed")
def reseed(
    workbook: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Re-run ingestion from the mounted spreadsheet (idempotent upsert)."""
    path = os.path.join(settings.frameworks_dir, workbook) if workbook else workbook_path()
    try:
        return run_seed(db, path)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
