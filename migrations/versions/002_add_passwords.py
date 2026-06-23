"""Add password_hash column to students table.

Revision ID: 002
Revises: 001
Create Date: 2026-06-23
"""
from collections.abc import Sequence
from typing import Union

from alembic import op

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
