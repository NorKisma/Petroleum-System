"""add petroleum morning automation settings

Revision ID: g9h4c2d5e7f8
Revises: f8a3b2c1d4e5
Create Date: 2026-06-10

"""
from alembic import op
import sqlalchemy as sa


revision = 'g9h4c2d5e7f8'
down_revision = 'f8a3b2c1d4e5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('petroleum_auto_morning_dip', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('petroleum_morning_auto_hour', sa.Integer(), nullable=True))
    op.execute("UPDATE tenants SET petroleum_auto_morning_dip = 1 WHERE petroleum_auto_morning_dip IS NULL")
    op.execute("UPDATE tenants SET petroleum_morning_auto_hour = 6 WHERE petroleum_morning_auto_hour IS NULL")


def downgrade():
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.drop_column('petroleum_morning_auto_hour')
        batch_op.drop_column('petroleum_auto_morning_dip')
