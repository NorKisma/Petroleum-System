"""add petroleum morning mode setting

Revision ID: h1i5d3e6f8g9
Revises: g9h4c2d5e7f8
Create Date: 2026-06-10

"""
from alembic import op
import sqlalchemy as sa


revision = 'h1i5d3e6f8g9'
down_revision = 'g9h4c2d5e7f8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('petroleum_morning_mode', sa.String(length=20), nullable=True))
    op.execute(
        "UPDATE tenants SET petroleum_morning_mode = 'manual' "
        "WHERE petroleum_auto_morning_dip = 0 AND petroleum_morning_mode IS NULL"
    )
    op.execute(
        "UPDATE tenants SET petroleum_morning_mode = 'automatic' "
        "WHERE petroleum_morning_mode IS NULL"
    )


def downgrade():
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.drop_column('petroleum_morning_mode')
