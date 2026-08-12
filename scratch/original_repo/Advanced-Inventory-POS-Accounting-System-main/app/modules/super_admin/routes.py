from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Tenant, User
from functools import wraps

super_admin = Blueprint('super_admin', __name__)

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_super_admin', False):
            flash('Access denied. Super Admin only.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@super_admin.route('/system-control')
@login_required
@super_admin_required
def system_dashboard():
    """Main dashboard for Super Admin to oversee all companies."""
    tenants = Tenant.query.all()
    total_tenants = len(tenants)
    active_tenants = Tenant.query.filter_by(subscription_status='active').count()
    expired_tenants = total_tenants - active_tenants
    
    return render_template('super_admin/dashboard.html', 
                           tenants=tenants,
                           total_tenants=total_tenants,
                           active_tenants=active_tenants,
                           expired_tenants=expired_tenants)

@super_admin.route('/system-control/tenant/<int:id>/subscription', methods=['POST'])
@login_required
@super_admin_required
def update_subscription(id):
    """Update a tenant's subscription plan and expiry."""
    tenant = Tenant.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'plan' in data:
            tenant.subscription_plan = data['plan']
        if 'status' in data:
            tenant.subscription_status = data['status']
        if 'expiry' in data:
            from datetime import datetime
            tenant.subscription_expiry = datetime.strptime(data['expiry'], '%Y-%m-%d')
            
        db.session.commit()
        return jsonify({'success': True, 'message': f'Subscription for {tenant.name} updated.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@super_admin.route('/system-control/tenant/<int:id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_tenant(id):
    """Hard delete a tenant (Warning: Deletes everything)."""
    tenant = Tenant.query.get_or_404(id)
    if tenant.subdomain == 'rays': # Protect system tenant
        return jsonify({'success': False, 'message': 'System tenant cannot be deleted.'})
    
    try:
        # Note: In a real app, you'd want to delete all related data or use a soft delete
        db.session.delete(tenant)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tenant deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
