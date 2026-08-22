from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

RESTRICTED_ROLES = ('cashier', 'staff', 'casheir')

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/landing.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Cashier and Staff go directly to Petroleum Sales — no app hub for them
    if current_user.role.lower() in RESTRICTED_ROLES:
        return redirect(url_for('petroleum.sales'))
    return render_template('main/apps.html', company_settings=current_user.tenant)
