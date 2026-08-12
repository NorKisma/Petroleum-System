from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Tenant, User, Sale, Product
from app.utils.decorators import roles_required
from sqlalchemy import func
from datetime import datetime

saas = Blueprint('saas', __name__)

def process_monthly_billing():
    """Check if a new month has started for any tenant and charge their monthly fee."""
    now = datetime.utcnow()
    tenants = Tenant.query.all()
    
    for t in tenants:
        if not t.last_billing_date:
            t.last_billing_date = t.created_at or t.start_date or now
            db.session.add(t)
            continue
            
        last_billing = t.last_billing_date
        months_diff = (now.year - last_billing.year) * 12 + (now.month - last_billing.month)
        
        if months_diff >= 1:
            for _ in range(months_diff):
                t.subscription_balance += t.monthly_fee
            
            t.subscription_status = 'Unpaid'
            t.last_billing_date = now
            db.session.add(t)
            
    db.session.commit()

@saas.route('/saas-management')
@login_required
@roles_required('developer')
def index():
    """Main dashboard for the system owner (Super Admin)."""
    process_monthly_billing()
    tenants = Tenant.query.all()
    
    # Calculate stats for each tenant
    tenant_stats = []
    for t in tenants:
        user_count = User.query.filter_by(tenant_id=t.id).count()
        sale_count = Sale.query.filter_by(tenant_id=t.id).count()
        product_count = Product.query.filter_by(tenant_id=t.id).count()
        
        # Financials
        from app.models import CustomerPayment, VendorPayment, Purchase
        total_sales = db.session.query(func.sum(Sale.total_amount)).filter_by(tenant_id=t.id).scalar() or 0
        total_received = db.session.query(func.sum(CustomerPayment.amount)).filter_by(tenant_id=t.id).scalar() or 0
        customer_debt = total_sales - total_received

        total_purchases = db.session.query(func.sum(Purchase.total_amount)).filter_by(tenant_id=t.id).scalar() or 0
        total_paid_to_vendors = db.session.query(func.sum(VendorPayment.amount)).filter_by(tenant_id=t.id).scalar() or 0
        vendor_debt = total_purchases - total_paid_to_vendors
        
        tenant_stats.append({
            'tenant': t,
            'user_count': user_count,
            'sale_count': sale_count,
            'product_count': product_count,
            'revenue': total_sales,
            'customer_debt': customer_debt,
            'vendor_debt': vendor_debt
        })
        
    total_tenants = len(tenants)
    total_users = User.query.count()
    overall_revenue = db.session.query(func.sum(Sale.total_amount)).scalar() or 0
    
    # Global Financials
    from app.models import CustomerPayment, VendorPayment, Purchase
    total_global_sales = db.session.query(func.sum(Sale.total_amount)).scalar() or 0
    total_global_received = db.session.query(func.sum(CustomerPayment.amount)).scalar() or 0
    global_customer_debt = total_global_sales - total_global_received
    
    # Subscription Stats
    total_sub_collected = sum(t.monthly_fee - t.subscription_balance for t in tenants)
    total_sub_pending = sum(t.subscription_balance for t in tenants)
    
    return render_template('saas/index.html', 
                           stats=tenant_stats,
                           total_tenants=total_tenants,
                           total_users=total_users,
                           overall_revenue=overall_revenue,
                           global_customer_debt=global_customer_debt,
                           total_sub_collected=total_sub_collected,
                           total_sub_pending=total_sub_pending)

@saas.route('/saas/tenant/<int:id>/collect-payment', methods=['POST'])
@login_required
@roles_required('developer')
def collect_tenant_payment(id):
    """Collect a payment (full or partial) from a tenant."""
    data = request.get_json()
    amount = float(data.get('amount', 0))
    
    tenant = Tenant.query.get_or_404(id)
    
    # Update balance
    tenant.subscription_balance -= amount
    if tenant.subscription_balance <= 0:
        tenant.subscription_status = 'Paid'
        tenant.subscription_balance = 0
    else:
        tenant.subscription_status = 'Partial'
        
    tenant.last_payment_date = datetime.utcnow()
    
    # Save the payment record
    from app.models import SaaSPayment
    import uuid
    payment_record = SaaSPayment(
        tenant_id=tenant.id,
        amount=amount,
        billing_period=datetime.utcnow().strftime("%B %Y"),
        reference_no=f"SAAS-PAY-{str(uuid.uuid4())[:8].upper()}"
    )
    db.session.add(payment_record)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Payment of ${amount} recorded for {tenant.name}!'})

@saas.route('/saas/tenant/<int:id>/payment-history')
@login_required
@roles_required('developer')
def tenant_payment_history(id):
    from app.models import SaaSPayment
    payments = SaaSPayment.query.filter_by(tenant_id=id).order_by(SaaSPayment.payment_date.desc()).all()
    
    history = []
    for p in payments:
        history.append({
            'date': p.payment_date.strftime('%Y-%m-%d %H:%M'),
            'amount': p.amount,
            'period': p.billing_period,
            'reference': p.reference_no
        })
    return jsonify(history)

@saas.route('/saas/tenant/<int:id>/toggle-status', methods=['POST'])
@login_required
@roles_required('developer')
def toggle_tenant_status(id):
    """Suspend or Activate all users of a tenant."""
    users = User.query.filter_by(tenant_id=id).all()
    # Logic: If at least one user is active, suspend all. Otherwise, activate all.
    any_active = any(u.is_active for u in users)
    
    for u in users:
        u.is_active = not any_active
    
    db.session.commit()
    status = "suspended" if any_active else "activated"
    return jsonify({'success': True, 'message': f'Shirkadda waa la {status}!'})

@saas.route('/saas/tenant/<int:id>/toggle-module', methods=['POST'])
@login_required
@roles_required('developer')
def toggle_tenant_module(id):
    """Toggle access to a specific module for a tenant."""
    data = request.get_json()
    module_name = data.get('module')
    
    tenant = Tenant.query.get_or_404(id)
    
    attr_name = f'module_{module_name}'
    if hasattr(tenant, attr_name):
        current_status = getattr(tenant, attr_name)
        setattr(tenant, attr_name, not current_status)
        status = not current_status
    else:
        return jsonify({'success': False, 'message': 'Invalid module!'})
        
    db.session.commit()
    state_str = "Furan (Enabled)" if status else "Xiran (Disabled)"
    return jsonify({'success': True, 'message': f'Module-ka waa la bedelay! Hadda waa: {state_str}'})

@saas.route('/saas/tenant/<int:id>/details')
@login_required
@roles_required('developer')
def tenant_details(id):
    """Get detailed information about a tenant."""
    tenant = Tenant.query.get_or_404(id)
    
    modules = {}
    for col in tenant.__table__.columns:
        if col.name.startswith('module_'):
            modules[col.name] = getattr(tenant, col.name)
            
    details = {
        'name': tenant.name,
        'email': tenant.email or 'N/A',
        'phone': tenant.phone or 'N/A',
        'address': tenant.address or 'N/A',
        'slogan': tenant.slogan or 'N/A',
        'created_at': tenant.created_at.strftime('%Y-%m-%d %H:%M'),
        'monthly_fee': tenant.monthly_fee
    }
    details.update(modules)
    return jsonify(details)

@saas.route('/saas/tenant/<int:id>/edit', methods=['POST'])
@login_required
@roles_required('developer')
def edit_tenant(id):
    """Edit tenant details."""
    tenant = Tenant.query.get_or_404(id)
    
    tenant.name = request.form.get('name')
    tenant.email = request.form.get('email')
    tenant.phone = request.form.get('phone')
    tenant.address = request.form.get('address')
    tenant.slogan = request.form.get('slogan')
    
    try:
        monthly_fee = float(request.form.get('monthly_fee', 15.0))
        tenant.monthly_fee = monthly_fee
    except ValueError:
        pass
        
    db.session.commit()
    flash(f"Shirkadda {tenant.name} si guul ah ayaa loo cusboonaysiiyay!", "success")
    return redirect(url_for('saas.index'))

@saas.route('/saas/tenant/add', methods=['POST'])
@login_required
@roles_required('developer')
def add_tenant():
    """Create a new Tenant and its initial Admin User."""
    from app import bcrypt
    from app.models import Tenant, User, Branch
    
    name = request.form.get('name')
    subdomain = request.form.get('subdomain')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    slogan = request.form.get('slogan')
    
    try:
        monthly_fee = float(request.form.get('monthly_fee', 15.0))
    except ValueError:
        monthly_fee = 15.0
        
    admin_username = request.form.get('admin_username')
    admin_email = request.form.get('admin_email')
    admin_password = request.form.get('admin_password')
    
    if not name or not subdomain or not admin_username or not admin_email or not admin_password:
        flash("Fadlan buuxi dhammaan macluumaadka khasabka ah!", "danger")
        return redirect(url_for('saas.index'))
        
    existing_tenant = Tenant.query.filter_by(subdomain=subdomain).first()
    if existing_tenant:
        flash("Subdomain-kani mar hore ayaa la isticmaalay! Fadlan dooro mid kale.", "danger")
        return redirect(url_for('saas.index'))
        
    existing_user = User.query.filter(
        (User.username == admin_username) | (User.email == admin_email)
    ).first()
    if existing_user:
        flash("Username-ka ama Email-ka maamulaha mar hore ayaa la isticmaalay!", "danger")
        return redirect(url_for('saas.index'))
        
    try:
        new_tenant = Tenant(
            name=name,
            subdomain=subdomain,
            email=email,
            phone=phone,
            address=address,
            slogan=slogan,
            monthly_fee=monthly_fee,
            subscription_status='Paid',
            subscription_balance=0.0,
            last_billing_date=datetime.utcnow()
        )
        db.session.add(new_tenant)
        db.session.flush()
        
        new_branch = Branch(
            name="Main Branch",
            location=address or "HQ",
            phone=phone,
            tenant_id=new_tenant.id
        )
        db.session.add(new_branch)
        db.session.flush()
        
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        new_admin = User(
            username=admin_username,
            email=admin_email,
            password=hashed_password,
            role='admin',
            phone=phone,
            tenant_id=new_tenant.id,
            branch_id=new_branch.id,
            is_active=True
        )
        db.session.add(new_admin)
        
        db.session.commit()
        flash(f"Shirkadda {name} iyo Maamulaheeda si guul ah ayaa loo abuuray!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Cillad ayaa dhacday: {str(e)}", "danger")
        
    return redirect(url_for('saas.index'))
