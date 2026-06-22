"""Modular parser interface and intermediate data structures.

A parser reads an .xlsx workbook and returns a `ParsedFramework` — a plain,
DB-agnostic structure. The seeder consumes it. To support a different workbook
layout, implement a new `WorkbookParser` and register it; nothing else changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class ParsedScaleOption:
    value: int
    label: str


@dataclass
class ParsedScale:
    key: str                       # deterministic, dedupes shared scales
    name: str                      # e.g. "Escala 0–3"
    min_value: int
    max_value: int
    options: list[ParsedScaleOption] = field(default_factory=list)


@dataclass
class ParsedQuestion:
    code: str
    text: str
    guidance: str | None = None
    weight: float = 1.0


@dataclass
class ParsedControl:
    code: str
    name: str
    questions: list[ParsedQuestion] = field(default_factory=list)


@dataclass
class ParsedDomain:
    key: str                       # worksheet name, e.g. "CTI"
    name: str                      # full title from row 1
    scale: ParsedScale
    reference_model: str | None = None
    maintainer: str | None = None
    scale_text: str | None = None
    reference_url: str | None = None
    controls: list[ParsedControl] = field(default_factory=list)


@dataclass
class ParsedFramework:
    slug: str
    name: str
    description: str | None = None
    source_file: str | None = None
    domains: list[ParsedDomain] = field(default_factory=list)


class WorkbookParser(Protocol):
    """Any parser that can turn a workbook path into a ParsedFramework."""

    def parse(self, path: str) -> ParsedFramework: ...
