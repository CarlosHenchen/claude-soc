"""Catalog (framework definition) models — populated by the spreadsheet seeder."""
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Framework(Base):
    __tablename__ = "frameworks"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)

    domains: Mapped[list["Domain"]] = relationship(
        back_populates="framework",
        cascade="all, delete-orphan",
        order_by="Domain.order_index",
    )


class Scale(Base):
    """A maturity scale. Each Domain references its own scale because the
    Viaconnect workbook uses a different scale per area (0-3, 0-4, 1-5, 0-5)."""

    __tablename__ = "scales"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    min_value: Mapped[int] = mapped_column(Integer)
    max_value: Mapped[int] = mapped_column(Integer)

    options: Mapped[list["ScaleOption"]] = relationship(
        back_populates="scale",
        cascade="all, delete-orphan",
        order_by="ScaleOption.value",
    )


class ScaleOption(Base):
    __tablename__ = "scale_options"
    __table_args__ = (UniqueConstraint("scale_id", "value", name="uq_scale_value"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scale_id: Mapped[int] = mapped_column(ForeignKey("scales.id", ondelete="CASCADE"))
    value: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(255))

    scale: Mapped[Scale] = relationship(back_populates="options")


class Domain(Base):
    __tablename__ = "domains"
    __table_args__ = (UniqueConstraint("framework_id", "key", name="uq_domain_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    framework_id: Mapped[int] = mapped_column(ForeignKey("frameworks.id", ondelete="CASCADE"))
    scale_id: Mapped[int] = mapped_column(ForeignKey("scales.id"))

    key: Mapped[str] = mapped_column(String(120), index=True)  # worksheet name, e.g. "CTI"
    name: Mapped[str] = mapped_column(String(500))             # full title from row 1
    reference_model: Mapped[str | None] = mapped_column(String(500), nullable=True)
    maintainer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scale_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reference_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    framework: Mapped[Framework] = relationship(back_populates="domains")
    scale: Mapped[Scale] = relationship()
    controls: Mapped[list["Control"]] = relationship(
        back_populates="domain",
        cascade="all, delete-orphan",
        order_by="Control.order_index",
    )


class Control(Base):
    """A subdomain group inside a domain (e.g. PROGRAM, ASSET, PREPARE...)."""

    __tablename__ = "controls"
    __table_args__ = (UniqueConstraint("domain_id", "code", name="uq_control_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(120))   # e.g. "PROGRAM"
    name: Mapped[str] = mapped_column(String(500))   # full header text
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    domain: Mapped[Domain] = relationship(back_populates="controls")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="control",
        cascade="all, delete-orphan",
        order_by="Question.order_index",
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(60), unique=True, index=True)  # e.g. "CTI-01"
    text: Mapped[str] = mapped_column(Text)
    guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Weighting factor for the weighted average. Spreadsheet uses equal weights,
    # so the default is 1.0; change per-question to weight differently.
    weight: Mapped[float] = mapped_column(Numeric(6, 3), default=1.0)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    control: Mapped[Control] = relationship(back_populates="questions")
