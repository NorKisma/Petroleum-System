"""
AI Intelligence Module — Enterprise ERP
Covers: Sales, Inventory, Purchasing, Customers, Expenses, HR
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Sale, SaleItem, Product, Purchase, Customer, User
from app.utils.ai_engine import (
    sales_insights, inventory_insights, purchasing_insights,
    customer_insights, hr_insights, business_health_score
)

# Try importing Expense model gracefully
try:
    from app.models import Expense
    HAS_EXPENSE = True
except ImportError:
    HAS_EXPENSE = False

from app.utils.ai_engine import expense_insights

ai = Blueprint('ai', __name__)


@ai.route('/ai')
@login_required
def dashboard():
    tid = current_user.tenant_id

    sales   = Sale.query.filter_by(tenant_id=tid).order_by(Sale.created_at.asc()).all()
    s_items = db.session.query(SaleItem).join(Sale).filter(Sale.tenant_id == tid).all()
    products = Product.query.filter_by(tenant_id=tid, is_active=True).all()
    purchases = Purchase.query.filter_by(tenant_id=tid).all()
    customers = Customer.query.filter_by(tenant_id=tid).all()
    staff    = User.query.filter_by(tenant_id=tid).all()

    expenses = []
    if HAS_EXPENSE:
        try:
            expenses = Expense.query.filter_by(tenant_id=tid).all()
        except Exception:
            pass

    # Run AI engines
    sales_data      = sales_insights(sales, s_items)
    inventory_data  = inventory_insights(products)
    purchasing_data = purchasing_insights(purchases)
    customer_data   = customer_insights(customers, sales)
    expense_data    = expense_insights(expenses)
    hr_data         = hr_insights(staff)
    health          = business_health_score(sales_data, inventory_data, customer_data, expense_data)

    return render_template('ai/dashboard.html',
        sales=sales_data,
        inventory=inventory_data,
        purchasing=purchasing_data,
        customers=customer_data,
        expenses=expense_data,
        hr=hr_data,
        health=health,
    )


@ai.route('/ai/api/summary')
@login_required
def api_summary():
    """JSON endpoint for live AI widget refresh."""
    tid = current_user.tenant_id
    sales   = Sale.query.filter_by(tenant_id=tid).all()
    s_items = db.session.query(SaleItem).join(Sale).filter(Sale.tenant_id == tid).all()
    products = Product.query.filter_by(tenant_id=tid, is_active=True).all()

    sd = sales_insights(sales, s_items)
    inv = inventory_insights(products)

    return jsonify({
        'trend': sd.get('trend'),
        'trend_pct': sd.get('trend_pct'),
        'forecast_7d': sd.get('forecast_7d'),
        'inv_score': inv.get('score'),
        'low_stock_count': len(inv.get('low_stock', [])),
        'recommendations': sd.get('recommendations', []) + inv.get('recommendations', [])
    })
