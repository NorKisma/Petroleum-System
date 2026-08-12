from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Tenant, User
import os
from werkzeug.utils import secure_filename
from app import bcrypt
from datetime import datetime

settings = Blueprint('settings', __name__)

@settings.route('/settings')
@login_required
def index():
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        flash('Ma haysatid ogolaansho aad ku gashid qaybtan.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    company = db.session.get(Tenant, current_user.tenant_id)
    return render_template('settings/index.html', company=company)

@settings.route('/settings/update', methods=['POST'])
@login_required
def update():
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        return redirect(url_for('settings.index'))
        
    company = db.session.get(Tenant, current_user.tenant_id)
    company.name = request.form.get('name')
    company.phone = request.form.get('phone')
    company.email = request.form.get('email')
    company.address = request.form.get('address')
    company.slogan = request.form.get('slogan')
    company.currency = request.form.get('currency', '$')
    company.tax_rate = float(request.form.get('tax_rate', 0.0))
    
    start_date_str = request.form.get('start_date_manual')
    if start_date_str:
        try:
            company.start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except:
            pass
    
    # Advanced Settings
    company.currency_symbol_placement = request.form.get('currency_symbol_placement', 'before')
    company.currency_precision = int(request.form.get('currency_precision', 2))
    company.quantity_precision = int(request.form.get('quantity_precision', 2))
    company.number_display_format = request.form.get('number_display_format', 'full')
    company.default_profit_percent = float(request.form.get('default_profit_percent', 25.0))
    company.stock_accounting_method = request.form.get('stock_accounting_method', 'FIFO')
    company.financial_year_start_month = request.form.get('financial_year_start_month', 'January')
    company.transaction_edit_days = int(request.form.get('transaction_edit_days', 30))
    company.timezone = request.form.get('timezone', 'Africa/Kampala')
    company.date_format = request.form.get('date_format', 'dd/mm/yyyy')
    company.time_format = request.form.get('time_format', '24 hour')
    
    # Product Settings
    company.sku_prefix = request.form.get('sku_prefix', 'SKU')
    company.enable_product_expiry = 'enable_product_expiry' in request.form
    company.expiry_action = request.form.get('expiry_action', 'keep')
    company.stock_expiry_alert_days = int(request.form.get('stock_expiry_alert_days', 30))
    company.enable_batch_number = 'enable_batch_number' in request.form
    
    # POS Settings
    company.disable_checkout_button = 'disable_checkout_button' in request.form
    company.enable_drafts = 'enable_drafts' in request.form
    company.pos_disable_discount = 'pos_disable_discount' in request.form
    company.pos_disable_tax = 'pos_disable_tax' in request.form
    company.pos_subtotal_editable = 'pos_subtotal_editable' in request.form
    company.pos_disable_multiple_pay = 'pos_disable_multiple_pay' in request.form
    company.pos_disable_express_checkout = 'pos_disable_express_checkout' in request.form
    company.pos_dont_show_product_suggestion = 'pos_dont_show_product_suggestion' in request.form
    company.pos_dont_show_recent_transactions = 'pos_dont_show_recent_transactions' in request.form
    company.pos_disable_suspend_sale = 'pos_disable_suspend_sale' in request.form
    company.pos_enable_transaction_date = 'pos_enable_transaction_date' in request.form
    company.pos_is_service_staff_required = 'pos_is_service_staff_required' in request.form
    company.pos_disable_credit_sale_button = 'pos_disable_credit_sale_button' in request.form
    company.pos_enable_weighing_scale = 'pos_enable_weighing_scale' in request.form
    company.order_prefix = request.form.get('order_prefix', 'ORD')
    
    # Email SMTP Settings
    company.email_host = request.form.get('email_host')
    try:
        val = request.form.get('email_port')
        company.email_port = int(val) if val else 587
    except ValueError:
        company.email_port = 587
    company.email_user = request.form.get('email_user')
    company.email_pass = request.form.get('email_pass')
    company.email_from_name = request.form.get('email_from_name')
    company.email_from_address = request.form.get('email_from_address')
    company.email_encryption = request.form.get('email_encryption', 'tls')
    
    # Module toggles are auto-saved via /settings/toggle-module (not this form).

    # Petroleum Settings
    company.petroleum_require_daily_dip = 'petroleum_require_daily_dip' in request.form
    company.petroleum_fleet_credit_enabled = 'petroleum_fleet_credit_enabled' in request.form
    company.petroleum_require_vehicle_plate = 'petroleum_require_vehicle_plate' in request.form
    morning_mode = request.form.get('petroleum_morning_mode', 'manual')
    if morning_mode not in ('automatic', 'manual'):
        morning_mode = 'manual'
    company.petroleum_morning_mode = morning_mode
    company.petroleum_auto_morning_dip = morning_mode == 'automatic'
    try:
        company.petroleum_morning_auto_hour = int(request.form.get('petroleum_morning_auto_hour', 6))
    except (TypeError, ValueError):
        company.petroleum_morning_auto_hour = 6
    try:
        company.petroleum_variance_threshold = float(request.form.get('petroleum_variance_threshold', 0.5))
    except ValueError:
        company.petroleum_variance_threshold = 0.5

    company.petroleum_shift1_name = request.form.get('petroleum_shift1_name') or 'Saaka (7AM-5PM)'
    company.petroleum_shift1_attendant = request.form.get('petroleum_shift1_attendant') or None
    company.petroleum_shift2_name = request.form.get('petroleum_shift2_name') or 'Habeen (5PM-7AM)'
    company.petroleum_shift2_attendant = request.form.get('petroleum_shift2_attendant') or None
    for field in ('petroleum_shift1_start_hour', 'petroleum_shift1_end_hour',
                  'petroleum_shift2_start_hour', 'petroleum_shift2_end_hour'):
        try:
            setattr(company, field, int(request.form.get(field, 0)))
        except (TypeError, ValueError):
            pass
    
    # SaaS & Sales Controls
    try:
        val = request.form.get('default_sale_discount', '0')
        company.default_sale_discount = float(val) if val else 0.0
    except ValueError:
        company.default_sale_discount = 0.0

    company.default_sale_tax = request.form.get('default_sale_tax')
    company.sales_item_addition_method = request.form.get('sales_item_addition_method', 'add_new')
    company.amount_rounding_method = request.form.get('amount_rounding_method', 'none')
    company.sales_price_is_minimum = 'sales_price_is_minimum' in request.form
    company.allow_overselling = 'allow_overselling' in request.form
    company.enable_sales_order = 'enable_sales_order' in request.form
    company.is_pay_term_required = 'is_pay_term_required' in request.form
    company.sales_commission_agent = request.form.get('sales_commission_agent', 'disable')
    company.commission_calculation_type = request.form.get('commission_calculation_type', 'percentage')
    company.is_commission_agent_required = 'is_commission_agent_required' in request.form
    company.enable_payment_link = 'enable_payment_link' in request.form
    company.razorpay_key_id = request.form.get('razorpay_key_id')
    company.razorpay_key_secret = request.form.get('razorpay_key_secret')
    company.stripe_public_key = request.form.get('stripe_public_key')
    company.stripe_secret_key = request.form.get('stripe_secret_key')
    
    # Handle Logo Upload
    file = request.files.get('logo')
    if file and file.filename != '':
        filename = secure_filename(f"logo_{company.id}_{file.filename}")
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        
        file.save(os.path.join(upload_path, filename))
        company.logo = f"uploads/logos/{filename}"
    
    try:
        db.session.commit()
        flash('Macluumaadka shirkadda waa la cusboonaysiiyay!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Khalad ayaa dhacay xiligii la keydinayay: {str(e)}', 'danger')
        
    return redirect(url_for('settings.index'))
MODULE_TOGGLE_FIELDS = {
    'module_purchases', 'module_pos', 'module_accounting', 'module_expenses',
    'module_stock_transfer', 'module_stock_adjustment', 'module_hrm',
    'module_service_staff', 'module_bookings', 'module_add_sale', 'module_tables',
    'module_modifiers', 'module_kitchen', 'module_subscription', 'module_types_of_service',
    'module_crm', 'module_manufacturing', 'module_project', 'module_assets',
    'module_repair', 'module_petroleum', 'module_share', 'module_sales',
    'module_customers', 'module_inventory',
}


@settings.route('/settings/toggle-module', methods=['POST'])
@login_required
def toggle_module():
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        return jsonify({'success': False, 'message': 'Ma haysatid ogolaansho.'}), 403

    data = request.get_json(silent=True) or {}
    field = data.get('module')
    if field not in MODULE_TOGGLE_FIELDS:
        return jsonify({'success': False, 'message': 'Module aan la aqoonsanayn.'}), 400

    company = db.session.get(Tenant, current_user.tenant_id)
    if not company:
        return jsonify({'success': False, 'message': 'Tenant lama helin.'}), 404

    enabled = data.get('enabled') in (True, 'true', '1', 1)
    setattr(company, field, enabled)
    try:
        db.session.commit()
        return jsonify({'success': True, 'module': field, 'enabled': enabled})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@settings.route('/settings/users')
@login_required
def manage_users():
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        flash('Ma haysatid ogolaansho.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    from app.models import User, Role
    users = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    roles = Role.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    # If no roles exist for this tenant, create defaults
    if not roles:
        admin_role = Role(name='Admin', tenant_id=current_user.tenant_id)
        cashier_role = Role(name='Cashier', tenant_id=current_user.tenant_id)
        db.session.add(admin_role)
        db.session.add(cashier_role)
        db.session.commit()
        roles = [admin_role, cashier_role]
        
    return render_template('settings/users.html', users=users, roles=roles)

@settings.route('/settings/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        return {'success': False, 'message': 'Unauthorized'}, 403
    
    from app.models import User
    from app import bcrypt
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'staff')
    
    if User.query.filter_by(username=username).first():
        flash('Username-kan waa la isticmaalay.', 'danger')
        return redirect(url_for('settings.manage_users'))
        
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        username=username,
        email=email,
        password=hashed_pw,
        role=role,
        tenant_id=current_user.tenant_id
    )
    db.session.add(new_user)
    db.session.commit()
    
    flash('User cusub ayaa lagu daray!', 'success')
    return redirect(url_for('settings.manage_users'))

@settings.route('/settings/users/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(id)
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    data = request.get_json()
    user.username = data.get('username')
    user.email = data.get('email')
    user.role = data.get('role')
    
    if data.get('password'):
        user.password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'User waa la cusboonaysiiyay!'})

@settings.route('/settings/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    if id == current_user.id:
        return jsonify({'success': False, 'message': 'Naftaada ma tirtiri kartid!'}), 400
        
    user = User.query.get_or_404(id)
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User waa la tirtiray!'})

@settings.route('/settings/roles/add', methods=['POST'])
@login_required
def add_role():
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    from app.models import Role
    name = request.form.get('name')
    if not name:
        flash('Role name is required!', 'danger')
        return redirect(url_for('settings.manage_users', view='roles'))
        
    new_role = Role(name=name, tenant_id=current_user.tenant_id)
    db.session.add(new_role)
    db.session.commit()
    
    flash(f'Role "{name}" ayaa lagu daray!', 'success')
    return redirect(url_for('settings.manage_users', view='roles'))

@settings.route('/settings/logs')
@login_required
def system_logs():
    if current_user.role not in ['developer'] and not getattr(current_user, 'is_super_admin', False):
        flash('Ma haysatid ogolaansho.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    from app.models import AuditLog
    logs = AuditLog.query.filter_by(tenant_id=current_user.tenant_id).order_by(AuditLog.created_at.desc()).limit(500).all()
    return render_template('settings/logs.html', logs=logs)
