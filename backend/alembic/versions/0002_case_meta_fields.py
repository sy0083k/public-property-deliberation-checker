"""add diagnosis case metadata fields

Revision ID: 0002_case_meta_fields
Revises: 0001_init
Create Date: 2026-02-13 00:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_case_meta_fields"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("diagnosis_case", sa.Column("project_name", sa.String(length=200), nullable=True))
    op.add_column("diagnosis_case", sa.Column("manager_name", sa.String(length=100), nullable=True))
    op.add_column("diagnosis_case", sa.Column("admin_phone", sa.String(length=30), nullable=True))

    op.execute("UPDATE diagnosis_case SET project_name = '미입력' WHERE project_name IS NULL")
    op.execute("UPDATE diagnosis_case SET manager_name = '미입력' WHERE manager_name IS NULL")
    op.execute("UPDATE diagnosis_case SET admin_phone = '미입력' WHERE admin_phone IS NULL")

    with op.batch_alter_table("diagnosis_case") as batch_op:
        batch_op.alter_column("project_name", nullable=False)
        batch_op.alter_column("manager_name", nullable=False)
        batch_op.alter_column("admin_phone", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("diagnosis_case") as batch_op:
        batch_op.drop_column("admin_phone")
        batch_op.drop_column("manager_name")
        batch_op.drop_column("project_name")
