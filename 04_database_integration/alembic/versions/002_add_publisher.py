"""Add publisher column to books

Revision ID: 002
Revises: 001
Create Date: 2026-02-14 12:30:00.000000

This migration demonstrates adding a new column to an existing table.
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add publisher column"""
    # Add the new column (nullable initially to allow existing records)
    op.add_column('books',
        sa.Column('publisher', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=True)
    )


def downgrade() -> None:
    """Remove publisher column"""
    op.drop_column('books', 'publisher')
