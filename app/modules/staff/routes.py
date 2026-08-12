from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import User
from app.utils.decorators import roles_required
from app.utils.audit import log_audit

staff = Blueprint('staff', __name__)

@staff.route('/staff')
@login_required
@roles_required('admin', 'developer')
def list_staff():
    members = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('staff/index.html', members=members)

@staff.route('/staff/add', methods=['POST'])
@login_required
@roles_required('admin', 'developer')
def add_member():
        
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'staff')
    phone = request.form.get('phone')
    salary = float(request.form.get('salary', 0.0))
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        flash('Email-kan hore ayaa loo isticmaalay!', 'danger')
        return redirect(url_for('staff.list_staff'))
        
    if User.query.filter_by(username=username).first():
        flash('Username-kan hore ayaa loo isticmaalay!', 'danger')
        return redirect(url_for('staff.list_staff'))
        
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        username=username,
        email=email,
        password=hashed_pw,
        role=role,
        phone=phone,
        salary=salary,
        tenant_id=current_user.tenant_id
    )
    db.session.add(new_user)
    db.session.commit()
    
    log_audit('ADD_STAFF', 'STAFF', f'Added new staff member: {username} ({role})')
    
    flash('Shaqaalaha waa la daray!', 'success')
    return redirect(url_for('staff.list_staff'))

@staff.route('/staff/edit/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'developer')
def edit_member(id):
        
    user = User.query.get_or_404(id)
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    # Allow full edit for admin and developer
        
    data = request.get_json()
    try:
        user.username = data.get('username', user.username)
        # Prevent logged-in user from changing their own role on the backend
        if user.id != current_user.id:
            user.role = data.get('role', user.role)
        user.phone = data.get('phone', user.phone)
        user.salary = float(data.get('salary', user.salary))
        
        # Don't change email or password from here to keep it simple, 
        # unless explicitly needed.
        
        db.session.commit()
        
        log_audit('EDIT_STAFF', 'STAFF', f'Updated profile for {user.username}. New role: {user.role}')
        
        return jsonify({'success': True, 'message': 'Shaqaalaha waa la cusboonaysiiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@staff.route('/staff/suspend/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'developer')
def suspend_member(id):
        
    user = User.query.get_or_404(id)
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    # Allow suspension for admin and developer
        
    # Prevent self-suspension
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Naftaada ma xannibi kartid!'}), 400
        
    try:
        user.is_active = not user.is_active
        db.session.commit()
        status_msg = 'Shaqaalaha waa la xannibay (Suspended)!' if not user.is_active else 'Shaqaalaha waa dib loo hawlgeliyay (Activated)!'
        
        log_audit('SUSPEND_STAFF' if not user.is_active else 'ACTIVATE_STAFF', 'STAFF', f'{status_msg} for {user.username}')
        
        return jsonify({'success': True, 'message': status_msg, 'is_active': user.is_active})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@staff.route('/staff/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'developer')
def delete_member(id):
        
    user = User.query.get_or_404(id)
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    # Allow deletion for admin and developer
        
    # Prevent self-deletion
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': 'Naftaada ma tirtiri kartid!'}), 400
        
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        log_audit('DELETE_STAFF', 'STAFF', f'Permanently deleted staff member: {username}')
        
        return jsonify({'success': True, 'message': 'Shaqaalaha si rasmi ah ayaa loo tirtiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@staff.route('/staff/user/<int:id>/modules', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'developer')
def manage_user_modules(id):
    user = User.query.get_or_404(id)
    
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    if request.method == 'GET':
        return jsonify({
            'module_pos': user.module_pos,
            'module_inventory': user.module_inventory,
            'module_accounting': user.module_accounting,
            'module_share': user.module_share,
            'module_sales': user.module_sales,
            'module_purchases': user.module_purchases,
            'module_customers': user.module_customers,
            'module_staff': user.module_staff,
            'module_settings': user.module_settings
        })
        
    # POST - Toggle module
    data = request.get_json()
    module_name = data.get('module')
    
    if module_name == 'pos':
        user.module_pos = not user.module_pos
        status = user.module_pos
    elif module_name == 'inventory':
        user.module_inventory = not user.module_inventory
        status = user.module_inventory
    elif module_name == 'accounting':
        user.module_accounting = not user.module_accounting
        status = user.module_accounting
    elif module_name == 'share':
        user.module_share = not user.module_share
        status = user.module_share
    elif module_name == 'sales':
        user.module_sales = not user.module_sales
        status = user.module_sales
    elif module_name == 'purchases':
        user.module_purchases = not user.module_purchases
        status = user.module_purchases
    elif module_name == 'customers':
        user.module_customers = not user.module_customers
        status = user.module_customers
    elif module_name == 'staff':
        user.module_staff = not user.module_staff
        status = user.module_staff
    elif module_name == 'settings':
        user.module_settings = not user.module_settings
        status = user.module_settings
    else:
        return jsonify({'success': False, 'message': 'Invalid module!'})
        
    db.session.commit()
    state_str = "Furan (Enabled)" if status else "Xiran (Disabled)"
    return jsonify({'success': True, 'message': f'Module-ka waa la bedelay! Hadda waa: {state_str}'})

# ── Payroll Management ────────────────────────────────────────────────────────

from app.models import Payroll
from datetime import datetime

@staff.route('/staff/payroll')
@login_required
@roles_required('admin', 'developer', 'accountant')
def list_payroll():
    # Get current month/year
    now = datetime.now()
    current_month = now.strftime('%B %Y')
    
    payroll_records = Payroll.query.filter_by(tenant_id=current_user.tenant_id).order_by(Payroll.created_at.desc()).all()
    
    # Calculate totals
    total_unpaid = sum(r.amount for r in payroll_records if r.status == 'pending')
    total_paid = sum(r.amount for r in payroll_records if r.status == 'paid')
    
    return render_template('staff/payroll.html', 
                           records=payroll_records, 
                           current_month=current_month,
                           total_unpaid=total_unpaid,
                           total_paid=total_paid)

@staff.route('/staff/payroll/generate', methods=['POST'])
@login_required
@roles_required('admin', 'developer', 'accountant')
def generate_payroll():
    now = datetime.now()
    month_str = now.strftime('%B %Y')
    
    # Check if payroll already exists for this month
    existing = Payroll.query.filter_by(tenant_id=current_user.tenant_id, month=month_str).first()
    if existing:
        return jsonify({'success': False, 'message': f'Payroll-ka bisha {month_str} hore ayaa loo soo saaray!'})
    
    active_staff = User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    
    count = 0
    for s in active_staff:
        if s.salary and s.salary > 0:
            new_record = Payroll(
                user_id=s.id,
                amount=s.salary,
                month=month_str,
                status='pending',
                tenant_id=current_user.tenant_id
            )
            db.session.add(new_record)
            count += 1
            
    db.session.commit()
    log_audit('GENERATE_PAYROLL', 'STAFF', f'Generated payroll for {month_str} ({count} staff members)')
    
    return jsonify({'success': True, 'message': f'Payroll-ka bisha {month_str} waa la soo saaray! ({count} qof)'})

@staff.route('/staff/payroll/pay/<int:id>', methods=['POST'])
@login_required
@roles_required('admin', 'developer', 'accountant')
def pay_staff(id):
    from app.models import Payroll, ChartAccount, JournalEntry, JournalLine
    
    record = Payroll.query.get_or_404(id)
    if record.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    if record.status == 'paid':
        return jsonify({'success': False, 'message': 'Hore ayaa loo bixiyay mushaharkan!'})
        
    try:
        # 1. Mark as Paid
        record.status = 'paid'
        record.paid_date = datetime.now()
        
        # 2. Automated Accounting Entry
        salary_expense = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, account_code='5200').first()
        cash_account = ChartAccount.query.filter_by(tenant_id=current_user.tenant_id, account_code='1000').first()
        
        if salary_expense and cash_account:
            # Create Journal Entry
            ref = f"PAY-{record.id}-{datetime.now().strftime('%y%m%d')}"
            entry = JournalEntry(
                reference=ref,
                description=f"Salary Payment: {record.user.username} for {record.month}",
                tenant_id=current_user.tenant_id
            )
            db.session.add(entry)
            db.session.flush() # Get ID
            
            # Debit: Salary Expense
            db.session.add(JournalLine(
                entry_id=entry.id,
                account_id=salary_expense.id,
                description=f"Salary Expense - {record.user.username}",
                debit=record.amount,
                credit=0.0
            ))
            
            # Credit: Cash
            db.session.add(JournalLine(
                entry_id=entry.id,
                account_id=cash_account.id,
                description=f"Cash Payment - {record.user.username}",
                debit=0.0,
                credit=record.amount
            ))
            
        db.session.commit()
        
        log_audit('PAY_STAFF', 'STAFF', f'Paid salary of ${record.amount} to {record.user.username} for {record.month}')
        
        return jsonify({'success': True, 'message': f'Mushaharka {record.user.username} waa la bixiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@staff.route('/staff/payroll/delete/<int:id>', methods=['DELETE'])
@login_required
@roles_required('admin', 'developer')
def delete_payroll(id):
    record = Payroll.query.get_or_404(id)
    if record.tenant_id != current_user.tenant_id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
        
    try:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Record-ka waa la tirtiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
