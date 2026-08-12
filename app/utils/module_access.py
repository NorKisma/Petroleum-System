"""Unified tenant + user module access checks."""

from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

# Short key → user column on User model (staff permission toggles)
USER_MODULE_FIELDS = {
    'pos': 'module_pos',
    'inventory': 'module_inventory',
    'accounting': 'module_accounting',
    'share': 'module_share',
    'sales': 'module_sales',
    'purchases': 'module_purchases',
    'customers': 'module_customers',
    'staff': 'module_staff',
    'settings': 'module_settings',
    'petroleum': 'module_petroleum',
    'expenses': 'module_expenses',
}

# App registry: key → access rules
MODULE_APPS = {
    'dashboards': {'always': True},
    'pos': {'tenant': 'module_pos', 'user': 'module_pos'},
    'sales': {
        'tenant_any': ['module_sales', 'module_add_sale', 'module_pos'],
        'user': 'module_sales',
    },
    'purchases': {'tenant': 'module_purchases', 'user': 'module_purchases'},
    'inventory': {'tenant': 'module_inventory', 'user': 'module_inventory'},
    'expenses': {'tenant': 'module_expenses', 'user': 'module_expenses'},
    'payroll': {'tenant': 'module_hrm', 'user': 'module_staff'},
    'contacts': {'tenant': 'module_customers', 'user': 'module_customers'},
    'accounting': {'tenant': 'module_accounting', 'user': 'module_accounting'},
    'reports': {'tenant': 'module_accounting', 'user': 'module_accounting'},
    'employees': {'tenant': 'module_hrm', 'user': 'module_staff', 'admin_only': True},
    'petroleum': {'tenant': 'module_petroleum', 'user': 'module_petroleum'},
    'share': {'tenant': 'module_share', 'user': 'module_share'},
    'settings': {'tenant': 'module_settings', 'user': 'module_settings', 'admin_only': True},
    'retail': {
        'tenant_any': [
            'module_bookings', 'module_tables', 'module_kitchen', 'module_subscription',
        ],
    },
    'erp': {
        'tenant_any': [
            'module_crm', 'module_manufacturing', 'module_project',
            'module_assets', 'module_repair',
        ],
    },
}

STAFF_MODULE_LABELS = {
    'pos': 'POS Terminal',
    'inventory': 'Inventory',
    'accounting': 'Accounting',
    'share': 'Shareholders',
    'sales': 'Sales Register',
    'purchases': 'Purchases',
    'customers': 'Customers',
    'staff': 'Staff & Payroll',
    'settings': 'System Settings',
    'petroleum': 'Petroleum / Fuel',
    'expenses': 'Expenses',
}


def user_is_privileged(user):
    return bool(
        user
        and user.is_authenticated
        and (getattr(user, 'is_super_admin', False) or user.role in ('admin', 'developer'))
    )


def _tenant_allows(tenant, cfg):
    if not tenant:
        return True
    if cfg.get('always'):
        return True
    tenant_any = cfg.get('tenant_any')
    if tenant_any:
        return any(getattr(tenant, attr, False) for attr in tenant_any)
    tenant_attr = cfg.get('tenant')
    if tenant_attr:
        return bool(getattr(tenant, tenant_attr, False))
    return True


def _user_allows(user, cfg):
    if user_is_privileged(user):
        return True
    user_attr = cfg.get('user')
    if user_attr:
        return bool(getattr(user, user_attr, False))
    return True


def can_access_module(user, tenant, module_key):
    if not user or not user.is_authenticated:
        return False
    cfg = MODULE_APPS.get(module_key)
    if not cfg:
        return False
    if cfg.get('admin_only') and not user_is_privileged(user):
        return False
    if not _tenant_allows(tenant, cfg):
        return False
    return _user_allows(user, cfg)


def get_user_module_permissions(user):
    return {key: bool(getattr(user, field, False)) for key, field in USER_MODULE_FIELDS.items()}


def toggle_user_module(user, module_key):
    field = USER_MODULE_FIELDS.get(module_key)
    if not field:
        return None
    current = bool(getattr(user, field, False))
    setattr(user, field, not current)
    return not current


def module_required(module_key, redirect_endpoint='main.dashboard'):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            from app.models import Tenant
            from app import db
            tenant = db.session.get(Tenant, current_user.tenant_id)
            if not can_access_module(current_user, tenant, module_key):
                flash('Ma haysatid ogolaansho aad ku gasho qaybtan.', 'danger')
                return redirect(url_for(redirect_endpoint))
            return f(*args, **kwargs)
        return wrapped
    return decorator
