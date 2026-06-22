from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..models import AssessmentStatus


class AssessmentCreate(BaseModel):
    framework_id: int
    name: str
    client: str | None = None
    assessor: str | None = None
    notes: str | None = None


class AssessmentUpdate(BaseModel):
    name: str | None = None
    client: str | None = None
    assessor: str | None = None
    notes: str | None = None
    status: AssessmentStatus | None = None


class AssessmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    framework_id: int
    name: str
    client: str | None
    assessor: str | None
    status: AssessmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ResponseInput(BaseModel):
    question_id: int
    current_value: int | None = None
    target_value: int | None = None
    evidence: str | None = None


class ResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question_id: int
    current_value: int | None
    target_value: int | None
    evidence: str | None
    gap: int | None
    updated_at: datetime


class AssessmentDetail(AssessmentOut):
    responses: list[ResponseOut]
