from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), unique=True, nullable=True)
    logo = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    slogan = db.Column(db.String(255), nullable=True)
    currency = db.Column(db.String(100), default='$') # Stores full name or symbol
    tax_rate = db.Column(db.Float, default=0.0)
    
    # New Advanced Settings
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    currency_symbol_placement = db.Column(db.String(20), default='before') # before, after
    currency_precision = db.Column(db.Integer, default=2)
    quantity_precision = db.Column(db.Integer, default=2)
    number_display_format = db.Column(db.String(20), default='full') # full, abbreviated
    default_profit_percent = db.Column(db.Float, default=25.0)
    stock_accounting_method = db.Column(db.String(20), default='FIFO') # FIFO, LIFO, Average
    financial_year_start_month = db.Column(db.String(20), default='January')
    transaction_edit_days = db.Column(db.Integer, default=30)
    timezone = db.Column(db.String(100), default='Africa/Kampala')
    date_format = db.Column(db.String(50), default='dd/mm/yyyy')
    time_format = db.Column(db.String(20), default='24 hour')
    
    # Product Settings
    sku_prefix = db.Column(db.String(10), default='SKU')
    enable_product_expiry = db.Column(db.Boolean, default=True)
    expiry_action = db.Column(db.String(20), default='keep') # keep, remove
    stock_expiry_alert_days = db.Column(db.Integer, default=30)
    enable_batch_number = db.Column(db.Boolean, default=True)
    
    # POS & Sale Settings
    pos_shortcuts = db.Column(db.JSON, nullable=True) 
    disable_checkout_button = db.Column(db.Boolean, default=False)
    enable_drafts = db.Column(db.Boolean, default=True)
    pos_disable_discount = db.Column(db.Boolean, default=False)
    pos_disable_tax = db.Column(db.Boolean, default=False)
    pos_subtotal_editable = db.Column(db.Boolean, default=True)
    pos_disable_multiple_pay = db.Column(db.Boolean, default=False)
    pos_disable_express_checkout = db.Column(db.Boolean, default=False)
    pos_dont_show_product_suggestion = db.Column(db.Boolean, default=False)
    pos_dont_show_recent_transactions = db.Column(db.Boolean, default=False)
    pos_disable_suspend_sale = db.Column(db.Boolean, default=False)
    pos_enable_transaction_date = db.Column(db.Boolean, default=True)
    pos_is_service_staff_required = db.Column(db.Boolean, default=False)
    pos_disable_credit_sale_button = db.Column(db.Boolean, default=False)
    pos_enable_weighing_scale = db.Column(db.Boolean, default=False)
    order_prefix = db.Column(db.String(10), default='ORD')
    
    # Email SMTP Settings
    email_host = db.Column(db.String(100), nullable=True)
    email_port = db.Column(db.Integer, default=587)
    email_user = db.Column(db.String(100), nullable=True)
    email_pass = db.Column(db.String(100), nullable=True)
    email_from_name = db.Column(db.String(100), nullable=True)
    email_from_address = db.Column(db.String(100), nullable=True)
    email_encryption = db.Column(db.String(10), default='tls') # tls, ssl
    
    # Billing & Subscription
    subscription_plan = db.Column(db.String(20), default='trial') # trial, basic, pro, enterprise
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    monthly_fee = db.Column(db.Float, default=15.0) 
    subscription_status = db.Column(db.String(20), default='active') # active, expired, suspended
    subscription_balance = db.Column(db.Float, default=0.0)
    last_payment_date = db.Column(db.DateTime, nullable=True)
    last_billing_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Modules Access
    module_pos = db.Column(db.Boolean, default=True)
    module_inventory = db.Column(db.Boolean, default=True)
    module_accounting = db.Column(db.Boolean, default=True)
    module_share = db.Column(db.Boolean, default=True)
    module_sales = db.Column(db.Boolean, default=True)
    module_purchases = db.Column(db.Boolean, default=True)
    module_customers = db.Column(db.Boolean, default=True)
    module_hrm = db.Column(db.Boolean, default=True)
    module_settings = db.Column(db.Boolean, default=True)
    module_expenses = db.Column(db.Boolean, default=True)
    module_stock_transfer = db.Column(db.Boolean, default=True)
    module_stock_adjustment = db.Column(db.Boolean, default=True)
    module_service_staff = db.Column(db.Boolean, default=False)
    module_bookings = db.Column(db.Boolean, default=False)
    module_add_sale = db.Column(db.Boolean, default=True)
    module_tables = db.Column(db.Boolean, default=False)
    module_modifiers = db.Column(db.Boolean, default=False)
    module_kitchen = db.Column(db.Boolean, default=False)
    module_subscription = db.Column(db.Boolean, default=False)
    module_types_of_service = db.Column(db.Boolean, default=False)
    
    # Advanced Enterprise Modules
    module_crm = db.Column(db.Boolean, default=False)
    module_manufacturing = db.Column(db.Boolean, default=False)
    module_project = db.Column(db.Boolean, default=False)
    module_assets = db.Column(db.Boolean, default=False)
    module_repair = db.Column(db.Boolean, default=False)
    module_petroleum = db.Column(db.Boolean, default=False)
    
    # Petroleum / Fuel Distribution Settings
    petroleum_require_daily_dip = db.Column(db.Boolean, default=True)
    petroleum_variance_threshold = db.Column(db.Float, default=0.5)
    petroleum_require_vehicle_plate = db.Column(db.Boolean, default=False)
    petroleum_fleet_credit_enabled = db.Column(db.Boolean, default=True)
    petroleum_auto_morning_dip = db.Column(db.Boolean, default=True)
    petroleum_morning_auto_hour = db.Column(db.Integer, default=6)
    petroleum_morning_mode = db.Column(db.String(20), default='automatic')  # automatic | manual
    petroleum_shift1_name = db.Column(db.String(100), default='Saaka (7AM-5PM)')
    petroleum_shift1_attendant = db.Column(db.String(100), nullable=True)
    petroleum_shift1_start_hour = db.Column(db.Integer, default=7)
    petroleum_shift1_end_hour = db.Column(db.Integer, default=17)
    petroleum_shift2_name = db.Column(db.String(100), default='Habeen (5PM-7AM)')
    petroleum_shift2_attendant = db.Column(db.String(100), nullable=True)
    petroleum_shift2_start_hour = db.Column(db.Integer, default=17)
    petroleum_shift2_end_hour = db.Column(db.Integer, default=7)
    
    # Sales & SaaS Controls
    default_sale_discount = db.Column(db.Float, default=0.0)
    default_sale_tax = db.Column(db.String(50), nullable=True)
    sales_item_addition_method = db.Column(db.String(50), default='add_new') # add_new, increase_qty
    amount_rounding_method = db.Column(db.String(50), default='none')
    sales_price_is_minimum = db.Column(db.Boolean, default=False)
    allow_overselling = db.Column(db.Boolean, default=False)
    enable_sales_order = db.Column(db.Boolean, default=False)
    is_pay_term_required = db.Column(db.Boolean, default=False)
    sales_commission_agent = db.Column(db.String(50), default='disable')
    commission_calculation_type = db.Column(db.String(50), default='percentage')
    is_commission_agent_required = db.Column(db.Boolean, default=False)
    enable_payment_link = db.Column(db.Boolean, default=False)
    razorpay_key_id = db.Column(db.String(255), nullable=True)
    razorpay_key_secret = db.Column(db.String(255), nullable=True)
    stripe_public_key = db.Column(db.String(255), nullable=True)
    stripe_secret_key = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='tenant', lazy=True)
    branches = db.relationship('Branch', backref='tenant', lazy=True)
    customers = db.relationship('Customer', backref='tenant', lazy=True)
    products = db.relationship('Product', backref='tenant', lazy='dynamic')
    categories = db.relationship('Category', backref='tenant', lazy='dynamic')

class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), default='staff') 
    phone = db.Column(db.String(20), nullable=True)
    salary = db.Column(db.Float, default=0.0)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)
    otp_code = db.Column(db.String(10), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    
    # User-level Module Permissions
    module_pos = db.Column(db.Boolean, default=True)
    module_inventory = db.Column(db.Boolean, default=True)
    module_accounting = db.Column(db.Boolean, default=True)
    module_share = db.Column(db.Boolean, default=True)
    module_sales = db.Column(db.Boolean, default=True)
    module_purchases = db.Column(db.Boolean, default=True)
    module_customers = db.Column(db.Boolean, default=True)
    module_staff = db.Column(db.Boolean, default=True)
    module_settings = db.Column(db.Boolean, default=True)
    module_petroleum = db.Column(db.Boolean, default=False)
    module_expenses = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    branch = db.relationship('Branch', backref='users')

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_group_id = db.Column(db.Integer, db.ForeignKey('customer_groups.id'), nullable=True)
    customer_group = db.relationship('CustomerGroup', backref='customers')

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False) 
    payment_account = db.Column(db.String(50), nullable=True) # Cash/Bank Account Code
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    branch = db.relationship('Branch', backref='expenses')
    fuel_shift_id = db.Column(db.Integer, db.ForeignKey('fuel_shifts.id'), nullable=True)
    fuel_day_close_id = db.Column(db.Integer, db.ForeignKey('fuel_day_closes.id'), nullable=True)
    
    fuel_shift = db.relationship('FuelShift', backref='expenses')
    fuel_day_close = db.relationship('FuelDayClose', backref='expenses')

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False) # e.g. EVC Plus, eDahab, Premier Bank
    account_number = db.Column(db.String(50), nullable=True)
    initial_balance = db.Column(db.Float, default=0.0)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    branch = db.relationship('Branch', backref='bank_accounts')

class BankTransfer(db.Model):
    __tablename__ = 'bank_transfers'
    id = db.Column(db.Integer, primary_key=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('chart_accounts.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('chart_accounts.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    from_account = db.relationship('ChartAccount', foreign_keys=[from_account_id], backref='transfers_out')
    to_account = db.relationship('ChartAccount', foreign_keys=[to_account_id], backref='transfers_in')

class ChartAccount(db.Model):
    __tablename__ = 'chart_accounts'
    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(20), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # ASSETS, LIABILITIES, REVENUE, EXPENSES, EQUITY
    sub_category = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True) # Professional addition for account descriptions
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    lines = db.relationship('JournalLine', backref='entry', cascade="all, delete-orphan", lazy=True)

class JournalLine(db.Model):
    __tablename__ = 'journal_lines'
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('chart_accounts.id'), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    
    account = db.relationship('ChartAccount', backref='journal_lines')

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='audit_logs')

class Payroll(db.Model):
    __tablename__ = 'payroll'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, paid
    paid_date = db.Column(db.DateTime, nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='payroll_records')
    fuel_shift_id = db.Column(db.Integer, db.ForeignKey('fuel_shifts.id'), nullable=True)
    
    fuel_shift = db.relationship('FuelShift', backref='payroll_items')


# ─── Petroleum / Fuel Distribution ───────────────────────────────────────────

class FuelType(db.Model):
    __tablename__ = 'fuel_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    color_code = db.Column(db.String(20), default='#f59e0b')
    buy_price = db.Column(db.Float, default=0.0)
    sell_price = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tanks = db.relationship('FuelTank', backref='fuel_type', lazy=True)
    pumps = db.relationship('FuelPump', backref='fuel_type', lazy=True)


class FuelTank(db.Model):
    __tablename__ = 'fuel_tanks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    capacity_liters = db.Column(db.Float, nullable=False, default=50000.0)
    current_level = db.Column(db.Float, default=0.0)
    min_alert_level = db.Column(db.Float, default=5000.0)
    last_dip_reading = db.Column(db.Float, nullable=True)
    last_dip_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branch = db.relationship('Branch', backref='fuel_tanks')
    pumps = db.relationship('FuelPump', backref='tank', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'fuel_type_id': self.fuel_type_id,
            'branch_id': self.branch_id,
            'capacity_liters': self.capacity_liters,
            'current_level': self.current_level,
            'min_alert_level': self.min_alert_level,
            'is_active': self.is_active,
        }


class FuelPump(db.Model):
    __tablename__ = 'fuel_pumps'
    id = db.Column(db.Integer, primary_key=True)
    pump_number = db.Column(db.String(50), nullable=False)
    selling_price = db.Column(db.Float, default=0.0)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    tank_id = db.Column(db.Integer, db.ForeignKey('fuel_tanks.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branch = db.relationship('Branch', backref='fuel_pumps')

    def to_dict(self):
        return {
            'id': self.id,
            'pump_number': self.pump_number,
            'selling_price': self.selling_price,
            'fuel_type_id': self.fuel_type_id,
            'tank_id': self.tank_id,
            'branch_id': self.branch_id,
            'is_active': self.is_active,
        }


class FleetProfile(db.Model):
    __tablename__ = 'fleet_profiles'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    fleet_code = db.Column(db.String(50), nullable=True)
    credit_limit = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    payment_terms_days = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('Customer', backref=db.backref('fleet_profile', uselist=False))


class FuelSale(db.Model):
    __tablename__ = 'fuel_sales'
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(50), nullable=False)
    pump_id = db.Column(db.Integer, db.ForeignKey('fuel_pumps.id'), nullable=True)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    tank_id = db.Column(db.Integer, db.ForeignKey('fuel_tanks.id'), nullable=False)
    liters_sold = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), default='Cash')
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    fleet_profile_id = db.Column(db.Integer, db.ForeignKey('fleet_profiles.id'), nullable=True)
    vehicle_plate = db.Column(db.String(50), nullable=True)
    driver_name = db.Column(db.String(100), nullable=True)
    meter_before = db.Column(db.Float, nullable=True)
    meter_after = db.Column(db.Float, nullable=True)
    attendant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    shift_number = db.Column(db.Integer, nullable=True)  # 1 or 2
    fuel_shift_id = db.Column(db.Integer, db.ForeignKey('fuel_shifts.id'), nullable=True)
    is_locked = db.Column(db.Boolean, default=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pump = db.relationship('FuelPump', backref='sales')
    fuel_type = db.relationship('FuelType', backref='sales')
    tank = db.relationship('FuelTank', backref='sales')
    customer = db.relationship('Customer', backref='fuel_sales')
    fleet_profile = db.relationship('FleetProfile', backref='fuel_sales')
    attendant = db.relationship('User', backref='fuel_sales_attended')
    branch = db.relationship('Branch', backref='fuel_sales')
    fuel_shift = db.relationship('FuelShift', backref='sales')


class FuelDelivery(db.Model):
    __tablename__ = 'fuel_deliveries'
    id = db.Column(db.Integer, primary_key=True)
    delivery_no = db.Column(db.String(50), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=True)
    purchase_name = db.Column(db.String(200), nullable=True)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    tank_id = db.Column(db.Integer, db.ForeignKey('fuel_tanks.id'), nullable=False)
    liters_received = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    waybill_no = db.Column(db.String(100), nullable=True)
    driver_name = db.Column(db.String(100), nullable=True)
    vehicle_no = db.Column(db.String(50), nullable=True)
    before_dip = db.Column(db.Float, nullable=True)
    after_dip = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(20), default='CREDIT')  # CASH or CREDIT
    is_locked = db.Column(db.Boolean, default=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    delivery_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor = db.relationship('Vendor', backref='fuel_deliveries')
    fuel_type = db.relationship('FuelType', backref='deliveries')
    tank = db.relationship('FuelTank', backref='deliveries')
    user = db.relationship('User', backref='fuel_deliveries')
    branch = db.relationship('Branch', backref='fuel_deliveries')


class FuelDeliveryPayment(db.Model):
    __tablename__ = 'fuel_delivery_payments'
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('fuel_deliveries.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=True)
    reference_no = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    delivery = db.relationship('FuelDelivery', backref=db.backref('payments', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref='fuel_delivery_payments')


class FuelDipReading(db.Model):
    __tablename__ = 'fuel_dip_readings'
    id = db.Column(db.Integer, primary_key=True)
    tank_id = db.Column(db.Integer, db.ForeignKey('fuel_tanks.id'), nullable=False)
    reading_liters = db.Column(db.Float, nullable=False)
    book_stock = db.Column(db.Float, nullable=False)
    variance = db.Column(db.Float, default=0.0)
    reading_type = db.Column(db.String(20), default='closing')
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    reading_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tank = db.relationship('FuelTank', backref='dip_readings')
    user = db.relationship('User', backref='fuel_dip_readings')
    branch = db.relationship('Branch', backref='fuel_dip_readings')


class FuelPriceHistory(db.Model):
    __tablename__ = 'fuel_price_history'
    id = db.Column(db.Integer, primary_key=True)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    old_buy_price = db.Column(db.Float, nullable=False)
    new_buy_price = db.Column(db.Float, nullable=False)
    old_sell_price = db.Column(db.Float, nullable=False)
    new_sell_price = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    effective_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    fuel_type = db.relationship('FuelType')

class FuelLoss(db.Model):
    __tablename__ = 'fuel_losses'
    id = db.Column(db.Integer, primary_key=True)
    log_date = db.Column(db.Date, nullable=False)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    tank_id = db.Column(db.Integer, db.ForeignKey('fuel_tanks.id'), nullable=False)
    liters_lost = db.Column(db.Float, nullable=False)
    loss_type = db.Column(db.String(50), default='Evaporation') # Leakage, Evaporation, Theft, Discrepancy
    notes = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    fuel_type = db.relationship('FuelType', backref='losses')
    tank = db.relationship('FuelTank', backref='losses')
    user = db.relationship('User', backref='recorded_losses')


class FuelStockLedger(db.Model):
    __tablename__ = 'fuel_stock_ledger'
    id = db.Column(db.Integer, primary_key=True)
    fuel_type_id = db.Column(db.Integer, db.ForeignKey('fuel_types.id'), nullable=False)
    tank_id = db.Column(db.Integer, db.ForeignKey('fuel_tanks.id'), nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False)
    reference_id = db.Column(db.Integer, nullable=True)
    reference_no = db.Column(db.String(50), nullable=True)
    liters_in = db.Column(db.Float, default=0.0)
    liters_out = db.Column(db.Float, default=0.0)
    balance_after = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    fuel_type = db.relationship('FuelType', backref='ledger_entries')
    tank = db.relationship('FuelTank', backref='ledger_entries')
    user = db.relationship('User', backref='fuel_ledger_entries')


class FuelPumpDailyLog(db.Model):
    __tablename__ = 'fuel_pump_daily_logs'
    id = db.Column(db.Integer, primary_key=True)
    pump_id = db.Column(db.Integer, db.ForeignKey('fuel_pumps.id'), nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    opening_meter = db.Column(db.Float, nullable=True)
    closing_meter = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pump = db.relationship('FuelPump', backref='daily_logs')
    user = db.relationship('User', backref='fuel_pump_logs')


class FuelPumpShiftLog(db.Model):
    __tablename__ = 'fuel_pump_shift_logs'
    id = db.Column(db.Integer, primary_key=True)
    pump_id = db.Column(db.Integer, db.ForeignKey('fuel_pumps.id'), nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    shift_number = db.Column(db.Integer, nullable=False)  # 1 or 2
    opening_meter = db.Column(db.Float, nullable=True)
    closing_meter = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attendant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    pump = db.relationship('FuelPump', backref='shift_logs')
    user = db.relationship('User', foreign_keys=[user_id], backref='fuel_pump_shift_logs')
    attendant = db.relationship('User', foreign_keys=[attendant_id], backref='attended_pump_logs')

    __table_args__ = (
        db.UniqueConstraint('pump_id', 'log_date', 'shift_number', 'tenant_id',
                            name='uq_fuel_pump_shift_log'),
    )


class FuelShift(db.Model):
    __tablename__ = 'fuel_shifts'
    id = db.Column(db.Integer, primary_key=True)
    log_date = db.Column(db.Date, nullable=False)
    shift_number = db.Column(db.Integer, nullable=False)
    attendant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='OPEN') # OPEN, CLOSED
    summary_data = db.Column(db.JSON, nullable=True) # Stores totals at closure
    notes = db.Column(db.Text, nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    attendant = db.relationship('User', backref='fuel_shifts_worked')
    tenant = db.relationship('Tenant', backref='fuel_shifts')

    __table_args__ = (
        db.UniqueConstraint('log_date', 'shift_number', 'tenant_id', name='uq_fuel_shift'),
    )


class FuelDayClose(db.Model):
    __tablename__ = 'fuel_day_closes'
    id = db.Column(db.Integer, primary_key=True)
    close_date = db.Column(db.Date, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    total_sales_liters = db.Column(db.Float, default=0.0)
    total_sales_amount = db.Column(db.Float, default=0.0)
    total_deliveries_liters = db.Column(db.Float, default=0.0)
    total_variance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='closed')
    notes = db.Column(db.Text, nullable=True)
    closed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branch = db.relationship('Branch', backref='fuel_day_closes')
    user = db.relationship('User', backref='fuel_day_closes')


# --- RESTORED POS MODELS FOR ACCOUNTING ---

class SaaSPayment(db.Model):
    __tablename__ = 'saas_payments'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    billing_period = db.Column(db.String(50), nullable=True) # e.g. "May 2026"
    reference_no = db.Column(db.String(100), nullable=True)
    
    tenant = db.relationship('Tenant', backref=db.backref('saas_payments_list', lazy=True))



class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)



class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)



class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    permissions = db.Column(db.JSON, nullable=True) 
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)



class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(50), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    buy_price = db.Column(db.Float, default=0.0)
    sell_price = db.Column(db.Float, default=0.0)
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Float, default=10.0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('Category', backref='products')
    unit = db.relationship('Unit', backref='products')
    brand = db.relationship('Brand', backref='products')



class CustomerGroup(db.Model):
    __tablename__ = 'customer_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calculation_percentage = db.Column(db.Float, default=0.0)
    selling_price_group = db.Column(db.String(100), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), default='AP') # AP or Cash
    ap_account = db.Column(db.String(100), nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    attachment = db.Column(db.String(255), nullable=True)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vendor = db.relationship('Vendor', backref='purchases')
    branch = db.relationship('Branch', backref='purchases')
    items = db.relationship('PurchaseItem', backref='purchase', cascade="all, delete-orphan", lazy=True)



class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=True)
    size = db.Column(db.String(50), nullable=True)



class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(50), unique=True, nullable=False)
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), default='Cash') 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    attachment = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='sales')
    branch = db.relationship('Branch', backref='sales')
    items = db.relationship('SaleItem', backref='sale', cascade="all, delete-orphan", lazy=True)



class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False) # Sale price back then
    buy_price = db.Column(db.Float, nullable=False)  # Buy price back then (for profit calc)
    size = db.Column(db.String(50), nullable=True)
    
    product = db.relationship('Product', backref='sold_items')

    def to_dict(self):
        return {
            'product_name': self.product.name if self.product else 'Unknown',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.quantity * self.unit_price
        }



class SaleReturn(db.Model):
    __tablename__ = 'sale_returns'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    invoice_no = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sale = db.relationship('Sale', backref='returns')
    items = db.relationship('SaleReturnItem', backref='sale_return', cascade="all, delete-orphan", lazy=True)



class SaleReturnItem(db.Model):
    __tablename__ = 'sale_return_items'
    id = db.Column(db.Integer, primary_key=True)
    sale_return_id = db.Column(db.Integer, db.ForeignKey('sale_returns.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)



class PurchaseReturn(db.Model):
    __tablename__ = 'purchase_returns'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    invoice_no = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    purchase = db.relationship('Purchase', backref='returns')
    items = db.relationship('PurchaseReturnItem', backref='purchase_return', cascade="all, delete-orphan", lazy=True)



class PurchaseReturnItem(db.Model):
    __tablename__ = 'purchase_return_items'
    id = db.Column(db.Integer, primary_key=True)
    purchase_return_id = db.Column(db.Integer, db.ForeignKey('purchase_returns.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)



class StockAdjustment(db.Model):
    __tablename__ = 'stock_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False) # Negative for loss/damage, Positive for found stock
    type = db.Column(db.String(50), nullable=False) # Damage, Loss, Found, Correction
    reason = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='adjustments')
    branch = db.relationship('Branch', backref='adjustments')



class StockTransfer(db.Model):
    __tablename__ = 'stock_transfers'
    id = db.Column(db.Integer, primary_key=True)
    reference_no = db.Column(db.String(50), nullable=False)
    from_branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    to_branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    status = db.Column(db.String(20), default='completed') # pending, completed
    shipping_charges = db.Column(db.Float, default=0.0)
    additional_notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    from_branch = db.relationship('Branch', foreign_keys=[from_branch_id], backref='transfers_out')
    to_branch = db.relationship('Branch', foreign_keys=[to_branch_id], backref='transfers_in')
    items = db.relationship('StockTransferItem', backref='transfer', cascade="all, delete-orphan")



class StockTransferItem(db.Model):
    __tablename__ = 'stock_transfer_items'
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('stock_transfers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=True)
    
    product = db.relationship('Product', backref='transfer_items')



class OtherIncome(db.Model):
    __tablename__ = 'other_incomes'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False) # Revenue Account Code
    account = db.Column(db.String(100), nullable=False)  # Bank/Cash Account Code
    income_date = db.Column(db.DateTime, default=datetime.utcnow)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class CustomerPayment(db.Model):
    __tablename__ = 'customer_payments'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='Cash')
    reference_no = db.Column(db.String(100), nullable=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='payments')



class VendorPayment(db.Model):
    __tablename__ = 'vendor_payments'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='Cash')
    reference_no = db.Column(db.String(100), nullable=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vendor = db.relationship('Vendor', backref='payments')



class Shareholder(db.Model):
    __tablename__ = 'shareholders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    investments = db.relationship('ShareInvestment', backref='shareholder', lazy=True)
    withdrawals = db.relationship('ShareWithdrawal', backref='shareholder', lazy=True)



class ShareInvestment(db.Model):
    __tablename__ = 'share_investments'
    id = db.Column(db.Integer, primary_key=True)
    shareholder_id = db.Column(db.Integer, db.ForeignKey('shareholders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    investment_date = db.Column(db.DateTime, default=datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('chart_accounts.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    account = db.relationship('ChartAccount', backref='share_investments')



class ShareWithdrawal(db.Model):
    __tablename__ = 'share_withdrawals'
    id = db.Column(db.Integer, primary_key=True)
    shareholder_id = db.Column(db.Integer, db.ForeignKey('shareholders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    withdrawal_date = db.Column(db.DateTime, default=datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('chart_accounts.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    account = db.relationship('ChartAccount', backref='share_withdrawals')



class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    depreciation_method = db.Column(db.String(50), default='None')
    useful_life_years = db.Column(db.Integer, default=0)
    salvage_value = db.Column(db.Float, default=0.0)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

