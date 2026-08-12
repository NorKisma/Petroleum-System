"""Add user-level petroleum module permission

Revision ID: e7f2a1b4c6d8
Revises: d4e8f1a2b3c5
Create Date: 2026-06-09 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e7f2a1b4c6d8'
down_revision = 'd4e8f1a2b3c5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('module_petroleum', sa.Boolean(), nullable=True))

    op.execute("UPDATE users SET module_petroleum = 0 WHERE module_petroleum IS NULL")
    op.execute(
        "UPDATE users SET module_petroleum = 1 "
        "WHERE role IN ('admin', 'developer') OR is_super_admin = 1"
    )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('module_petroleum')
