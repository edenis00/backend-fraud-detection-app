"""merge heads: ff79553e084f and 1a2b3c4d5e6f

Revision ID: merge_0001
Revises: ff79553e084f, 1a2b3c4d5e6f
Create Date: 2026-09-26 00:10:00.000000

This is an automatic merge migration to resolve multiple heads created by parallel branches.
"""
from alembic import op
from typing import Union, Sequence

# revision identifiers, used by Alembic.
revision: str = 'merge_0001'
down_revision: Union[str, Sequence[str], None] = ('ff79553e084f', '1a2b3c4d5e6f')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # no schema changes; this merge revision consolidates branches
    pass


def downgrade() -> None:
    # no-op: downgrading a merge requires manual handling
    pass
