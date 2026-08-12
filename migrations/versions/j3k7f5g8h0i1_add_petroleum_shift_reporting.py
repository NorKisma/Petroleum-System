"""add petroleum shift reporting

Revision ID: j3k7f5g8h0i1
Revises: i2j6e4f7g9h0
Create Date: 2026-06-13

"""
from alembic import op
import sqlalchemy as sa


revision = 'j3k7f5g8h0i1'
down_revision = 'i2j6e4f7g9h0'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column already exists in the given table."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :table AND column_name = :col"
        ),
        {"table": table_name, "col": column_name}
    )
    return result.scalar() > 0


def table_exists(table_name):
    """Check if a table already exists."""
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :table"
        ),
        {"table": table_name}
    )
    return result.scalar() > 0


def upgrade():
    # Add columns to tenants table only if they don't already exist
    tenant_columns = [
        ('petroleum_shift1_name', sa.String(length=100)),
        ('petroleum_shift1_attendant', sa.String(length=100)),
        ('petroleum_shift1_start_hour', sa.Integer()),
        ('petroleum_shift1_end_hour', sa.Integer()),
        ('petroleum_shift2_name', sa.String(length=100)),
        ('petroleum_shift2_attendant', sa.String(length=100)),
        ('petroleum_shift2_start_hour', sa.Integer()),
        ('petroleum_shift2_end_hour', sa.Integer()),
    ]

    for col_name, col_type in tenant_columns:
        if not column_exists('tenants', col_name):
            op.add_column('tenants', sa.Column(col_name, col_type, nullable=True))

    # Add shift_number to fuel_sales if it doesn't exist
    if not column_exists('fuel_sales', 'shift_number'):
        op.add_column('fuel_sales', sa.Column('shift_number', sa.Integer(), nullable=True))

    # Create fuel_pump_shift_logs table if it doesn't exist
    if not table_exists('fuel_pump_shift_logs'):
        op.create_table('fuel_pump_shift_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('pump_id', sa.Integer(), nullable=False),
            sa.Column('log_date', sa.Date(), nullable=False),
            sa.Column('shift_number', sa.Integer(), nullable=False),
            sa.Column('opening_meter', sa.Float(), nullable=True),
            sa.Column('closing_meter', sa.Float(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('tenant_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['pump_id'], ['fuel_pumps.id']),
            sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('pump_id', 'log_date', 'shift_number', 'tenant_id',
                                name='uq_fuel_pump_shift_log')
        )


def downgrade():
    op.drop_table('fuel_pump_shift_logs')
    with op.batch_alter_table('fuel_sales', schema=None) as batch_op:
        batch_op.drop_column('shift_number')
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.drop_column('petroleum_shift2_end_hour')
        batch_op.drop_column('petroleum_shift2_start_hour')
        batch_op.drop_column('petroleum_shift2_attendant')
        batch_op.drop_column('petroleum_shift2_name')
        batch_op.drop_column('petroleum_shift1_end_hour')
        batch_op.drop_column('petroleum_shift1_start_hour')
        batch_op.drop_column('petroleum_shift1_attendant')
        batch_op.drop_column('petroleum_shift1_name')
