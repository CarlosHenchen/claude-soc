"""ORM models for the SOC maturity instrument.

Faithful mapping of the Viaconnect Health Check workbook:

    Framework  -> the whole instrument ("Viaconnect Health Check SOC")
    Domain     -> each worksheet / assessment area (9 domains)
    Control    -> a subdomain group inside a worksheet (e.g. PROGRAM, ASSET)
    Question   -> an individual assessment item (CTI-01 ... AU-09)
    Scale      -> the maturity scale of a Domain (each domain has its own!)

Plus the runtime entities: User, Assessment, Response, Score.
"""
from .catalog import Control, Domain, Framework, Question, Scale, ScaleOption
from .assessment import Assessment, AssessmentStatus, Response, Score, ScoreScope
from .user import User

__all__ = [
    "Framework",
    "Domain",
    "Control",
    "Question",
    "Scale",
    "ScaleOption",
    "User",
    "Assessment",
    "AssessmentStatus",
    "Response",
    "Score",
    "ScoreScope",
]
