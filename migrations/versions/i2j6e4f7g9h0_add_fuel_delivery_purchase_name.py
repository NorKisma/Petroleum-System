"""add purchase_name to fuel deliveries

Revision ID: i2j6e4f7g9h0
Revises: h1i5d3e6f8g9
Create Date: 2026-06-10

"""
from alembic import op
import sqlalchemy as sa


revision = 'i2j6e4f7g9h0'
down_revision = 'h1i5d3e6f8g9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('fuel_deliveries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('purchase_name', sa.String(length=200), nullable=True))


def downgrade():
    with op.batch_alter_table('fuel_deliveries', schema=None) as batch_op:
        batch_op.drop_column('purchase_name')
