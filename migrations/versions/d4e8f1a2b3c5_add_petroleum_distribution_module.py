"""Add petroleum distribution module

Revision ID: d4e8f1a2b3c5
Revises: cc0293142c0d
Create Date: 2026-06-09 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e8f1a2b3c5'
down_revision = 'cc0293142c0d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('module_petroleum', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('petroleum_require_daily_dip', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('petroleum_variance_threshold', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('petroleum_require_vehicle_plate', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('petroleum_fleet_credit_enabled', sa.Boolean(), nullable=True))

    op.execute("UPDATE tenants SET module_petroleum = 0 WHERE module_petroleum IS NULL")
    op.execute("UPDATE tenants SET petroleum_require_daily_dip = 1 WHERE petroleum_require_daily_dip IS NULL")
    op.execute("UPDATE tenants SET petroleum_variance_threshold = 0.5 WHERE petroleum_variance_threshold IS NULL")
    op.execute("UPDATE tenants SET petroleum_require_vehicle_plate = 1 WHERE petroleum_require_vehicle_plate IS NULL")
    op.execute("UPDATE tenants SET petroleum_fleet_credit_enabled = 1 WHERE petroleum_fleet_credit_enabled IS NULL")

    op.create_table('fuel_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('color_code', sa.String(length=20), nullable=True),
        sa.Column('buy_price', sa.Float(), nullable=True),
        sa.Column('sell_price', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fleet_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('fleet_code', sa.String(length=50), nullable=True),
        sa.Column('credit_limit', sa.Float(), nullable=True),
        sa.Column('current_balance', sa.Float(), nullable=True),
        sa.Column('payment_terms_days', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_tanks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('fuel_type_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('capacity_liters', sa.Float(), nullable=False),
        sa.Column('current_level', sa.Float(), nullable=True),
        sa.Column('min_alert_level', sa.Float(), nullable=True),
        sa.Column('last_dip_reading', sa.Float(), nullable=True),
        sa.Column('last_dip_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['fuel_type_id'], ['fuel_types.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fuel_type_id', sa.Integer(), nullable=False),
        sa.Column('old_buy_price', sa.Float(), nullable=False),
        sa.Column('new_buy_price', sa.Float(), nullable=False),
        sa.Column('old_sell_price', sa.Float(), nullable=False),
        sa.Column('new_sell_price', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=False),
        sa.Column('effective_date', sa.DateTime(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['fuel_type_id'], ['fuel_types.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_day_closes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('close_date', sa.Date(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('total_sales_liters', sa.Float(), nullable=True),
        sa.Column('total_sales_amount', sa.Float(), nullable=True),
        sa.Column('total_deliveries_liters', sa.Float(), nullable=True),
        sa.Column('total_variance', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('closed_by', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['closed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_pumps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pump_number', sa.String(length=50), nullable=False),
        sa.Column('fuel_type_id', sa.Integer(), nullable=False),
        sa.Column('tank_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['fuel_type_id'], ['fuel_types.id']),
        sa.ForeignKeyConstraint(['tank_id'], ['fuel_tanks.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('delivery_no', sa.String(length=50), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        sa.Column('fuel_type_id', sa.Integer(), nullable=False),
        sa.Column('tank_id', sa.Integer(), nullable=False),
        sa.Column('liters_received', sa.Float(), nullable=False),
        sa.Column('unit_cost', sa.Float(), nullable=False),
        sa.Column('total_cost', sa.Float(), nullable=False),
        sa.Column('waybill_no', sa.String(length=100), nullable=True),
        sa.Column('driver_name', sa.String(length=100), nullable=True),
        sa.Column('vehicle_no', sa.String(length=50), nullable=True),
        sa.Column('before_dip', sa.Float(), nullable=True),
        sa.Column('after_dip', sa.Float(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('delivery_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['fuel_type_id'], ['fuel_types.id']),
        sa.ForeignKeyConstraint(['tank_id'], ['fuel_tanks.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_dip_readings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tank_id', sa.Integer(), nullable=False),
        sa.Column('reading_liters', sa.Float(), nullable=False),
        sa.Column('book_stock', sa.Float(), nullable=False),
        sa.Column('variance', sa.Float(), nullable=True),
        sa.Column('reading_type', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('reading_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['tank_id'], ['fuel_tanks.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_stock_ledger',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fuel_type_id', sa.Integer(), nullable=False),
        sa.Column('tank_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=30), nullable=False),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('reference_no', sa.String(length=50), nullable=True),
        sa.Column('liters_in', sa.Float(), nullable=True),
        sa.Column('liters_out', sa.Float(), nullable=True),
        sa.Column('balance_after', sa.Float(), nullable=False),
        sa.Column('unit_cost', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['fuel_type_id'], ['fuel_types.id']),
        sa.ForeignKeyConstraint(['tank_id'], ['fuel_tanks.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_pump_daily_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pump_id', sa.Integer(), nullable=False),
        sa.Column('log_date', sa.Date(), nullable=False),
        sa.Column('opening_meter', sa.Float(), nullable=True),
        sa.Column('closing_meter', sa.Float(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['pump_id'], ['fuel_pumps.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fuel_sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_no', sa.String(length=50), nullable=False),
        sa.Column('pump_id', sa.Integer(), nullable=True),
        sa.Column('fuel_type_id', sa.Integer(), nullable=False),
        sa.Column('tank_id', sa.Integer(), nullable=False),
        sa.Column('liters_sold', sa.Float(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('payment_method', sa.String(length=20), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('fleet_profile_id', sa.Integer(), nullable=True),
        sa.Column('vehicle_plate', sa.String(length=50), nullable=True),
        sa.Column('driver_name', sa.String(length=100), nullable=True),
        sa.Column('meter_before', sa.Float(), nullable=True),
        sa.Column('meter_after', sa.Float(), nullable=True),
        sa.Column('attendant_id', sa.Integer(), nullable=True),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_locked', sa.Boolean(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('sale_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['attendant_id'], ['users.id']),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['fleet_profile_id'], ['fleet_profiles.id']),
        sa.ForeignKeyConstraint(['fuel_type_id'], ['fuel_types.id']),
        sa.ForeignKeyConstraint(['pump_id'], ['fuel_pumps.id']),
        sa.ForeignKeyConstraint(['tank_id'], ['fuel_tanks.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('fuel_sales')
    op.drop_table('fuel_pump_daily_logs')
    op.drop_table('fuel_stock_ledger')
    op.drop_table('fuel_dip_readings')
    op.drop_table('fuel_deliveries')
    op.drop_table('fuel_pumps')
    op.drop_table('fuel_day_closes')
    op.drop_table('fuel_price_history')
    op.drop_table('fuel_tanks')
    op.drop_table('fleet_profiles')
    op.drop_table('fuel_types')
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.drop_column('petroleum_fleet_credit_enabled')
        batch_op.drop_column('petroleum_require_vehicle_plate')
        batch_op.drop_column('petroleum_variance_threshold')
        batch_op.drop_column('petroleum_require_daily_dip')
        batch_op.drop_column('module_petroleum')
