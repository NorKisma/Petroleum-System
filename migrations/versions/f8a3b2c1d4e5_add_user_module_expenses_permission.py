"""Add user-level expenses module permission

Revision ID: f8a3b2c1d4e5
Revises: e7f2a1b4c6d8
Create Date: 2026-06-09 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f8a3b2c1d4e5'
down_revision = 'e7f2a1b4c6d8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('module_expenses', sa.Boolean(), nullable=True))

    op.execute("UPDATE users SET module_expenses = 1 WHERE module_expenses IS NULL")


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('module_expenses')
