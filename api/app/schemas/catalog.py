from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ScaleOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    value: int
    label: str


class ScaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    key: str
    name: str
    min_value: int
    max_value: int
    options: list[ScaleOptionOut]


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    text: str
    guidance: str | None
    weight: float
    order_index: int


class ControlOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    order_index: int
    questions: list[QuestionOut]


class DomainOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    key: str
    name: str
    reference_model: str | None
    maintainer: str | None
    scale_text: str | None
    reference_url: str | None
    order_index: int
    scale: ScaleOut


class DomainDetail(DomainOut):
    controls: list[ControlOut]


class FrameworkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    description: str | None
    source_file: str | None


class FrameworkDetail(FrameworkOut):
    domains: list["DomainDetail"]
