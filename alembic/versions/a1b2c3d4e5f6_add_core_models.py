"""add core models: departments, cards, fraud_rules, audit_logs and extend transactions

Revision ID: a1b2c3d4e5f6
Revises: 48734ea09525
Create Date: 2026-09-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '48734ea09525'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create departments table
    op.create_table('departments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('department_code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('department_code')
    )
    op.create_index(op.f('ix_departments_department_code'), 'departments', ['department_code'], unique=True)
    op.create_index(op.f('ix_departments_status'), 'departments', ['status'], unique=False)

    # Create cards table
    op.create_table('cards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_reference', sa.String(length=100), nullable=False),
    sa.Column('masked_card_number', sa.String(length=20), nullable=False),
    sa.Column('department_id', sa.Integer(), nullable=False),
    sa.Column('assigned_user_id', sa.Integer(), nullable=True),
    sa.Column('card_type', sa.String(length=50), nullable=False),
    sa.Column('issue_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
    sa.ForeignKeyConstraint(['assigned_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('card_reference')
    )
    op.create_index(op.f('ix_cards_assigned_user_id'), 'cards', ['assigned_user_id'], unique=False)
    op.create_index(op.f('ix_cards_card_reference'), 'cards', ['card_reference'], unique=True)
    op.create_index(op.f('ix_cards_department_id'), 'cards', ['department_id'], unique=False)
    op.create_index(op.f('ix_cards_status'), 'cards', ['status'], unique=False)

    # Create fraud_rules table
    op.create_table('fraud_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rule_code', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('threshold', sa.Float(), nullable=False),
    sa.Column('severity', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('rule_code')
    )
    op.create_index(op.f('ix_fraud_rules_rule_code'), 'fraud_rules', ['rule_code'], unique=True)
    op.create_index(op.f('ix_fraud_rules_status'), 'fraud_rules', ['status'], unique=False)
    op.create_index(op.f('ix_fraud_rules_severity'), 'fraud_rules', ['severity'], unique=False)

    # Create audit_logs table
    op.create_table('audit_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('entity_type', sa.String(length=100), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_entity_type'), 'audit_logs', ['entity_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)

    # Extend transactions table
    op.add_column('transactions', sa.Column('card_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('department_id', sa.Integer(), nullable=True))
    op.add_column('transactions', sa.Column('merchant', sa.String(length=255), nullable=True))
    op.add_column('transactions', sa.Column('currency', sa.String(length=8), nullable=False, server_default='NGN'))
    op.add_column('transactions', sa.Column('description', sa.Text(), nullable=True))
    
    op.create_foreign_key('fk_transactions_card_id', 'transactions', 'cards', ['card_id'], ['id'])
    op.create_foreign_key('fk_transactions_department_id', 'transactions', 'departments', ['department_id'], ['id'])
    op.create_index(op.f('ix_transactions_card_id'), 'transactions', ['card_id'], unique=False)
    op.create_index(op.f('ix_transactions_department_id'), 'transactions', ['department_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indices and constraints from transactions
    op.drop_index(op.f('ix_transactions_department_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_card_id'), table_name='transactions')
    op.drop_constraint('fk_transactions_department_id', 'transactions', type_='foreignkey')
    op.drop_constraint('fk_transactions_card_id', 'transactions', type_='foreignkey')
    
    # Drop columns from transactions
    op.drop_column('transactions', 'description')
    op.drop_column('transactions', 'currency')
    op.drop_column('transactions', 'merchant')
    op.drop_column('transactions', 'department_id')
    op.drop_column('transactions', 'card_id')
    
    # Drop new tables
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_entity_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index(op.f('ix_fraud_rules_severity'), table_name='fraud_rules')
    op.drop_index(op.f('ix_fraud_rules_status'), table_name='fraud_rules')
    op.drop_index(op.f('ix_fraud_rules_rule_code'), table_name='fraud_rules')
    op.drop_table('fraud_rules')
    
    op.drop_index(op.f('ix_cards_status'), table_name='cards')
    op.drop_index(op.f('ix_cards_department_id'), table_name='cards')
    op.drop_index(op.f('ix_cards_card_reference'), table_name='cards')
    op.drop_index(op.f('ix_cards_assigned_user_id'), table_name='cards')
    op.drop_table('cards')
    
    op.drop_index(op.f('ix_departments_status'), table_name='departments')
    op.drop_index(op.f('ix_departments_department_code'), table_name='departments')
    op.drop_table('departments')
