"""Add password_hash column to students table.

Revision ID: 002
Revises: 001
Create Date: 2026-06-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE students
        ADD COLUMN password_hash VARCHAR(256) NULL
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE students
        DROP COLUMN password_hash
    """)
