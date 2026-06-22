"""Runtime assessment models: Assessment, Response and persisted Score snapshots."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class AssessmentStatus(str, enum.Enum):
    draft = "draft"
    in_progress = "in_progress"
    completed = "completed"


class ScoreScope(str, enum.Enum):
    overall = "overall"
    domain = "domain"
    control = "control"


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    framework_id: Mapped[int] = mapped_column(ForeignKey("frameworks.id"))
    name: Mapped[str] = mapped_column(String(255))
    client: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assessor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[AssessmentStatus] = mapped_column(
        Enum(AssessmentStatus, name="assessment_status"), default=AssessmentStatus.draft
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    responses: Mapped[list["Response"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    scores: Mapped[list["Score"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (
        UniqueConstraint("assessment_id", "question_id", name="uq_response_assessment_question"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), index=True
    )
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    # Current and target maturity levels (numeric value of the chosen dropdown option).
    current_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    assessment: Mapped[Assessment] = relationship(back_populates="responses")

    @property
    def gap(self) -> int | None:
        if self.current_value is None or self.target_value is None:
            return None
        return self.target_value - self.current_value


class Score(Base):
    """Persisted snapshot of a computed score (overall / per-domain / per-control)."""

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), index=True
    )
    scope: Mapped[ScoreScope] = mapped_column(Enum(ScoreScope, name="score_scope"))
    # scope_id points at a domain id or control id; null for the overall score.
    scope_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scope_label: Mapped[str | None] = mapped_column(String(500), nullable=True)

    raw_score: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    normalized_pct: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    target_raw: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    target_pct: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    gap: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    answered: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    assessment: Mapped[Assessment] = relationship(back_populates="scores")
