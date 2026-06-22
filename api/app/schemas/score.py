from __future__ import annotations

from pydantic import BaseModel


class ScoreOut(BaseModel):
    scope: str                  # overall | domain | control
    scope_id: int | None
    label: str | None
    raw_score: float | None     # mean maturity level (in the scale's own units)
    normalized_pct: float | None  # raw_score normalized to 0-100% of the scale max
    target_raw: float | None
    target_pct: float | None
    gap: float | None           # target_raw - raw_score
    scale_min: int | None
    scale_max: int | None
    answered: int
    total: int


class ControlScoreOut(ScoreOut):
    pass


class DomainScoreOut(ScoreOut):
    controls: list[ControlScoreOut] = []


class DashboardOut(BaseModel):
    assessment_id: int
    overall: ScoreOut
    domains: list[DomainScoreOut]
