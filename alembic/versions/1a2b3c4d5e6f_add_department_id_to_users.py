"""add department_id to users

Revision ID: 1a2b3c4d5e6f
Revises: a1b2c3d4e5f6
Create Date: 2026-09-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = inspector.get_table_names()

    if 'departments' not in existing:
        op.create_table(
            'departments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('department_code', sa.String(length=50), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('department_code'),
        )
        op.create_index(op.f('ix_departments_department_code'), 'departments', ['department_code'], unique=True)
        op.create_index(op.f('ix_departments_status'), 'departments', ['status'], unique=False)

    if 'department_id' not in sa.inspect(bind).get_columns('users'):
        op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True))

    op.create_index(op.f('ix_users_department_id'), 'users', ['department_id'], unique=False)
    op.create_foreign_key('fk_users_department_id', 'users', 'departments', ['department_id'], ['id'])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'department_id' in [c['name'] for c in inspector.get_columns('users')]:
        op.drop_constraint('fk_users_department_id', 'users', type_='foreignkey')
        op.drop_index(op.f('ix_users_department_id'), table_name='users')
        op.drop_column('users', 'department_id')
