"""widen users phone for formatted international numbers

Revision ID: f2c4e6a8b0d1
Revises: e5b1c7d8a9f0
Create Date: 2026-09-24 15:45:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "f2c4e6a8b0d1"
down_revision = "e5b1c7d8a9f0"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "users",
        "phone",
        existing_type=sa.String(length=15),
        type_=sa.String(length=32),
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        "users",
        "phone",
        existing_type=sa.String(length=32),
        type_=sa.String(length=15),
        existing_nullable=True,
    )
