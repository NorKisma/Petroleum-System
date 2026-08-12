from flask import Blueprint, render_template, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
import os
from app.models import Product, Sale, SaleItem, Expense, Customer, Vendor, Purchase, CustomerPayment, VendorPayment, OtherIncome
from sqlalchemy import func
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('main/landing.html')

@main.route('/privacy-policy')
def privacy_policy():
    return render_template('main/privacy_policy.html')

@main.route('/.well-known/assetlinks.json')
def serve_assetlinks():
    return send_from_directory(os.path.join(current_app.root_path, 'static', '.well-known'), 'assetlinks.json', mimetype='application/json')

@main.route('/analytics')
@login_required
def analytics():
    tid = current_user.tenant_id
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())

    from app.services.accounting_service import AccountingService
    summary = AccountingService.get_financial_summary(tid)
    total_sales = summary['revenue']

    # ── Today's Sales ─────────────────────────────────────────────────────────
    today_sales = db.session.query(func.sum(Sale.total_amount))\
        .filter(Sale.tenant_id == tid, Sale.created_at >= today_start).scalar() or 0.0
    today_orders = Sale.query.filter(Sale.tenant_id == tid,
                                     Sale.created_at >= today_start).count()

    # ── Total Orders ──────────────────────────────────────────────────────────
    total_orders = Sale.query.filter_by(tenant_id=tid).count()

    # ── Low Stock ─────────────────────────────────────────────────────────────
    low_stock_query = Product.query.filter_by(tenant_id=tid)\
        .filter(Product.stock_quantity <= Product.low_stock_threshold)
    low_stock_count = low_stock_query.count()
    low_stock_items = low_stock_query.limit(5).all()

    # ── Accounting Stats ──────────────────────────────────────────────────────
    cogs = summary['cogs']
    total_expenses = summary['expenses']
    net_profit = summary['net_profit']
    total_purchases = db.session.query(func.sum(Purchase.total_amount)).filter_by(tenant_id=tid).scalar() or 0.0
    
    # ── Returns ───────────────────────────────────────────────────────────────
    from app.models import SaleReturn, PurchaseReturn
    total_sell_returns = db.session.query(func.sum(SaleReturn.total_amount)).filter_by(tenant_id=tid).scalar() or 0.0
    total_purchase_returns = db.session.query(func.sum(PurchaseReturn.total_amount)).filter_by(tenant_id=tid).scalar() or 0.0

    # ── Pending AR (Accounts Receivable) ─────────────────────────────────────
    pending_ar = AccountingService.get_account_balance(
        AccountingService.get_account('1100', tid).id if AccountingService.get_account('1100', tid) else 0,
        tid
    )

    # ── Pending AP (Accounts Payable) ─────────────────────────────────────────
    pending_ap = AccountingService.get_account_balance(
        AccountingService.get_account('2000', tid).id if AccountingService.get_account('2000', tid) else 0,
        tid
    )

    # ── 7-Day Sales Chart Data ─────────────────────────────────────────────────
    chart_labels = []
    chart_data   = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end   = datetime.combine(day, datetime.max.time())
        day_total = db.session.query(func.sum(Sale.total_amount))\
            .filter(Sale.tenant_id == tid,
                    Sale.created_at >= day_start,
                    Sale.created_at <= day_end).scalar() or 0.0
        chart_labels.append(day.strftime('%a %d'))
        chart_data.append(round(day_total, 2))

    # ── Top 5 Products by Revenue ─────────────────────────────────────────────
    top_products_raw = db.session.query(
        Product.name,
        func.sum(SaleItem.quantity).label('qty'),
        func.sum(SaleItem.quantity * SaleItem.unit_price).label('revenue')
    ).join(SaleItem, SaleItem.product_id == Product.id)\
     .join(Sale, Sale.id == SaleItem.sale_id)\
     .filter(Sale.tenant_id == tid)\
     .group_by(Product.id)\
     .order_by(func.sum(SaleItem.quantity * SaleItem.unit_price).desc())\
     .limit(5).all()

    top_products = [{'name': r.name, 'qty': r.qty, 'revenue': round(r.revenue, 2)}
                    for r in top_products_raw]

    # ── Recent Sales ───────────────────────────────────────────────────────────
    recent_sales = Sale.query.filter_by(tenant_id=tid)\
        .order_by(Sale.created_at.desc()).limit(8).all()

    # ── AI Health Insights (Lightweight Heuristic) ────────────────────────────
    try:
        health = 80
        if total_sales > total_expenses: health += 5
        else: health -= 10
        if low_stock_count > 0: health -= min(low_stock_count * 2, 15)
        if pending_ap > 5000: health -= 5
        if pending_ar > 1000: health -= 2
        health = max(0, min(100, health))
        
        if health >= 85: grade, color = 'A', '#10b981'
        elif health >= 70: grade, color = 'B', '#3b82f6'
        elif health >= 55: grade, color = 'C', '#f59e0b'
        else: grade, color = 'D', '#ef4444'
        
        ai_health = {'score': round(health), 'grade': grade, 'color': color}
    except Exception:
        ai_health = None

    stats = {
        'total_sales':   total_sales,
        'today_sales':   today_sales,
        'today_orders':  today_orders,
        'total_orders':  total_orders,
        'low_stock':     low_stock_count,
        'total_revenue': total_sales,
        'net_profit':    net_profit,
        'total_purchase': total_purchases,
        'total_purchase_return': total_purchase_returns,
        'total_sell_return': total_sell_returns,
        'total_expenses': total_expenses,
        'pending_ar':    pending_ar,
        'pending_ap':    pending_ap,
    }

    return render_template('main/dashboard.html',
                           stats=stats,
                           recent_sales=recent_sales,
                           top_products=top_products,
                           low_stock_items=low_stock_items,
                           chart_labels=chart_labels,
                           chart_data=chart_data,
                           ai_health=ai_health,
                           tenant=current_user.tenant,
                           datetime_utcnow=datetime.utcnow)

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/apps.html',
                           company_settings=current_user.tenant)

