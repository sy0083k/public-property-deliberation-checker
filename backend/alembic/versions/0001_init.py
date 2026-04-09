"""init

Revision ID: 0001_init
Revises:
Create Date: 2026-02-13 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "diagnosis_case",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("municipality_code", sa.String(length=30), nullable=False),
        sa.Column("final_decision", sa.String(length=40), nullable=True),
        sa.Column("final_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_diagnosis_case_created_at", "diagnosis_case", ["created_at"])
    op.create_index("ix_diagnosis_case_final_decision", "diagnosis_case", ["final_decision"])
    op.create_index("ix_diagnosis_case_department", "diagnosis_case", ["department"])

    op.create_table(
        "diagnosis_answer",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("diagnosis_case.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_code", sa.String(length=40), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("case_id", "question_code", name="uq_case_question"),
    )

    op.create_table(
        "diagnosis_trace",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("diagnosis_case.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_key", sa.String(length=20), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "rule_profile",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("municipality_code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_rule_profile_municipality_active",
        "rule_profile",
        ["municipality_code", "is_active"],
    )


def downgrade() -> None:
    op.drop_index("ix_rule_profile_municipality_active", table_name="rule_profile")
    op.drop_table("rule_profile")
    op.drop_table("diagnosis_trace")
    op.drop_table("diagnosis_answer")
    op.drop_index("ix_diagnosis_case_department", table_name="diagnosis_case")
    op.drop_index("ix_diagnosis_case_final_decision", table_name="diagnosis_case")
    op.drop_index("ix_diagnosis_case_created_at", table_name="diagnosis_case")
    op.drop_table("diagnosis_case")
