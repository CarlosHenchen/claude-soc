"""Spreadsheet ingestion package (openpyxl-based, modular parsers)."""
from .base import ParsedFramework, WorkbookParser
from .seeder import run_seed, seed_admin, seed_framework, workbook_path
from .viaconnect_parser import ViaconnectParser

__all__ = [
    "ParsedFramework",
    "WorkbookParser",
    "ViaconnectParser",
    "run_seed",
    "seed_admin",
    "seed_framework",
    "workbook_path",
]
