"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "frameworks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("source_file", sa.String(255)),
    )
    op.create_index("ix_frameworks_slug", "frameworks", ["slug"])

    op.create_table(
        "scales",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("key", sa.String(120), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("min_value", sa.Integer, nullable=False),
        sa.Column("max_value", sa.Integer, nullable=False),
    )
    op.create_index("ix_scales_key", "scales", ["key"])

    op.create_table(
        "scale_options",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("scale_id", sa.Integer, sa.ForeignKey("scales.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value", sa.Integer, nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.UniqueConstraint("scale_id", "value", name="uq_scale_value"),
    )

    op.create_table(
        "domains",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("framework_id", sa.Integer, sa.ForeignKey("frameworks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scale_id", sa.Integer, sa.ForeignKey("scales.id"), nullable=False),
        sa.Column("key", sa.String(120), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("reference_model", sa.String(500)),
        sa.Column("maintainer", sa.String(500)),
        sa.Column("scale_text", sa.String(255)),
        sa.Column("reference_url", sa.Text),
        sa.Column("order_index", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("framework_id", "key", name="uq_domain_key"),
    )
    op.create_index("ix_domains_key", "domains", ["key"])

    op.create_table(
        "controls",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("domain_id", sa.Integer, sa.ForeignKey("domains.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(120), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("order_index", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("domain_id", "code", name="uq_control_code"),
    )

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("control_id", sa.Integer, sa.ForeignKey("controls.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(60), nullable=False, unique=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("guidance", sa.Text),
        sa.Column("weight", sa.Numeric(6, 3), nullable=False, server_default="1.0"),
        sa.Column("order_index", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index("ix_questions_code", "questions", ["code"])

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(120), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255)),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_username", "users", ["username"])

    assessment_status = sa.Enum("draft", "in_progress", "completed", name="assessment_status")
    score_scope = sa.Enum("overall", "domain", "control", name="score_scope")

    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("framework_id", sa.Integer, sa.ForeignKey("frameworks.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("client", sa.String(255)),
        sa.Column("assessor", sa.String(255)),
        sa.Column("status", assessment_status, nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text),
        sa.Column("created_by_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "responses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("assessment_id", sa.Integer, sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Integer, sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("current_value", sa.Integer),
        sa.Column("target_value", sa.Integer),
        sa.Column("evidence", sa.Text),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("assessment_id", "question_id", name="uq_response_assessment_question"),
    )
    op.create_index("ix_responses_assessment_id", "responses", ["assessment_id"])
    op.create_index("ix_responses_question_id", "responses", ["question_id"])

    op.create_table(
        "scores",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("assessment_id", sa.Integer, sa.ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope", score_scope, nullable=False),
        sa.Column("scope_id", sa.Integer),
        sa.Column("scope_label", sa.String(500)),
        sa.Column("raw_score", sa.Numeric(6, 3)),
        sa.Column("normalized_pct", sa.Numeric(6, 2)),
        sa.Column("target_raw", sa.Numeric(6, 3)),
        sa.Column("target_pct", sa.Numeric(6, 2)),
        sa.Column("gap", sa.Numeric(6, 3)),
        sa.Column("answered", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_scores_assessment_id", "scores", ["assessment_id"])


def downgrade() -> None:
    op.drop_table("scores")
    op.drop_table("responses")
    op.drop_table("assessments")
    op.drop_table("users")
    op.drop_table("questions")
    op.drop_table("controls")
    op.drop_table("domains")
    op.drop_table("scale_options")
    op.drop_table("scales")
    op.drop_table("frameworks")
    sa.Enum(name="assessment_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="score_scope").drop(op.get_bind(), checkfirst=True)
