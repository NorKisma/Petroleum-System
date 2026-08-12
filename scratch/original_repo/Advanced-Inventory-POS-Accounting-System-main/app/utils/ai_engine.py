"""
Enterprise AI Engine — Rays Technology Center
Covers: Sales, Inventory, Purchasing, HR/Staff, Accounting, Customers, Expenses
No external ML library required — pure data analysis + statistical inference.
"""
from datetime import datetime, timedelta
from collections import defaultdict


# ─────────────────────────────────────────────
# SALES MODULE AI
# ─────────────────────────────────────────────

def sales_insights(sales, sale_items):
    """Full sales intelligence: trend, forecast, top products, margins."""
    if not sales:
        return {
            'total_revenue': 0, 'avg_daily': 0, 'trend': 'stable',
            'trend_pct': 0, 'forecast_7d': 0, 'top_products': [],
            'peak_hour': 'N/A', 'recommendations': ['Add sales data to get AI insights.']
        }

    today = datetime.today().date()
    daily = defaultdict(float)
    hourly = defaultdict(int)

    for s in sales:
        day = s.created_at.strftime('%Y-%m-%d')
        daily[day] += float(s.total_amount or 0)
        hourly[s.created_at.hour] += 1

    past_30 = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    values_30 = [daily.get(str(d), 0.0) for d in past_30]

    past_7_vals = values_30[-7:]
    prev_7_vals = values_30[-14:-7]

    this_week = sum(past_7_vals)
    last_week = sum(prev_7_vals) or 1
    trend_pct = round(((this_week - last_week) / last_week) * 100, 1)
    trend = 'up' if trend_pct > 3 else ('down' if trend_pct < -3 else 'stable')

    slope = _slope(values_30)
    forecast_7d = round(max(0, sum(values_30[-7:]) + slope * 7), 2)
    avg_daily = round(sum(values_30) / 30, 2)

    # Top products
    prod_qty = defaultdict(lambda: {'qty': 0, 'rev': 0.0})
    for item in sale_items:
        name = item.product.name if item.product else 'Unknown'
        prod_qty[name]['qty'] += item.quantity
        prod_qty[name]['rev'] += float(item.quantity * item.unit_price)
    top_products = sorted(
        [{'name': k, **v} for k, v in prod_qty.items()],
        key=lambda x: x['rev'], reverse=True
    )[:5]

    # Peak hour
    peak_hour = max(hourly, key=hourly.get) if hourly else None
    peak_label = f"{peak_hour}:00 - {peak_hour+1}:00" if peak_hour is not None else 'N/A'

    # Recommendations
    recs = []
    if trend == 'down':
        recs.append('⚠️ Sales dropped this week. Consider a promotion or discount campaign.')
    if trend == 'up':
        recs.append('✅ Sales are growing! Ensure sufficient stock to meet demand.')
    if avg_daily < 50:
        recs.append('💡 Daily revenue is low. Review pricing strategy and product visibility.')
    if peak_hour and (peak_hour < 9 or peak_hour > 17):
        recs.append(f'🕐 Peak sales at {peak_label}. Schedule more staff during this time.')
    if not recs:
        recs.append('✅ Sales performance is stable. Keep monitoring trends.')

    return {
        'total_revenue': round(sum(daily.values()), 2),
        'avg_daily': avg_daily,
        'trend': trend,
        'trend_pct': trend_pct,
        'forecast_7d': forecast_7d,
        'top_products': top_products,
        'peak_hour': peak_label,
        'recommendations': recs,
        'historical': [{'date': str(d), 'amount': daily.get(str(d), 0.0)} for d in past_30],
    }


# ─────────────────────────────────────────────
# INVENTORY MODULE AI
# ─────────────────────────────────────────────

def inventory_insights(products):
    """Inventory health: low stock, dead stock, overstock, reorder alerts."""
    if not products:
        return {'score': 100, 'low_stock': [], 'dead_stock': [], 'overstock': [], 'recommendations': []}

    low_stock, dead_stock, overstock = [], [], []
    today = datetime.today().date()

    for p in products:
        qty = p.stock_quantity or 0
        threshold = p.low_stock_threshold or 10

        if qty == 0:
            low_stock.append({'name': p.name, 'qty': 0, 'threshold': threshold, 'severity': 'critical'})
        elif qty <= threshold:
            low_stock.append({'name': p.name, 'qty': qty, 'threshold': threshold, 'severity': 'warning'})

        # Dead stock: has inventory but never sold or sold very long ago
        last_sold = None
        if hasattr(p, 'sold_items') and p.sold_items:
            try:
                last_sold = max(si.sale.created_at.date() for si in p.sold_items)
            except Exception:
                pass
        days_since = (today - last_sold).days if last_sold else 9999
        if qty > 0 and days_since >= 60:
            dead_stock.append({
                'name': p.name,
                'qty': qty,
                'value': round(qty * float(p.buy_price or 0), 2),
                'days_idle': days_since if days_since < 9999 else 'Never sold'
            })

        # Overstock: more than 5x threshold
        if qty > threshold * 5:
            overstock.append({'name': p.name, 'qty': qty, 'threshold': threshold})

    total = len(products)
    healthy = total - len(low_stock) - len([d for d in dead_stock if d['days_idle'] != 'Never sold'])
    score = max(0, round((healthy / total) * 100)) if total > 0 else 100

    recs = []
    critical = [x for x in low_stock if x['severity'] == 'critical']
    if critical:
        recs.append(f'🚨 {len(critical)} product(s) are OUT OF STOCK. Reorder immediately!')
    if low_stock:
        recs.append(f'⚠️ {len(low_stock)} product(s) below reorder threshold.')
    if dead_stock:
        recs.append(f'💤 {len(dead_stock)} product(s) are slow/dead stock. Consider discounting or returning to supplier.')
    if overstock:
        recs.append(f'📦 {len(overstock)} product(s) are overstocked. Pause reordering to reduce holding costs.')
    if not recs:
        recs.append('✅ Inventory health is excellent! All products are well-stocked.')

    return {
        'score': score,
        'low_stock': low_stock[:10],
        'dead_stock': dead_stock[:10],
        'overstock': overstock[:10],
        'total_products': total,
        'recommendations': recs
    }


# ─────────────────────────────────────────────
# PURCHASING MODULE AI
# ─────────────────────────────────────────────

def purchasing_insights(purchases):
    """Vendor spend analysis, payment trends, AP health."""
    if not purchases:
        return {'total_spend': 0, 'top_vendors': [], 'ap_pending': 0, 'recommendations': []}

    vendor_spend = defaultdict(float)
    ap_pending = 0.0
    monthly = defaultdict(float)

    for p in purchases:
        vendor_name = p.vendor.name if p.vendor else 'Unknown'
        amount = float(p.total_amount or 0)
        vendor_spend[vendor_name] += amount
        if p.payment_method == 'AP':
            ap_pending += amount
        month = p.created_at.strftime('%Y-%m')
        monthly[month] += amount

    top_vendors = sorted(
        [{'name': k, 'spend': round(v, 2)} for k, v in vendor_spend.items()],
        key=lambda x: x['spend'], reverse=True
    )[:5]

    recs = []
    if ap_pending > 10000:
        recs.append(f'⚠️ High AP balance: ${ap_pending:,.2f}. Schedule vendor payments to avoid late fees.')
    if len(vendor_spend) == 1:
        recs.append('💡 Single-vendor dependency detected. Diversify suppliers to reduce risk.')
    if not recs:
        recs.append('✅ Purchasing patterns look healthy.')

    return {
        'total_spend': round(sum(vendor_spend.values()), 2),
        'top_vendors': top_vendors,
        'ap_pending': round(ap_pending, 2),
        'vendor_count': len(vendor_spend),
        'recommendations': recs
    }


# ─────────────────────────────────────────────
# CUSTOMER MODULE AI
# ─────────────────────────────────────────────

def customer_insights(customers, sales):
    """Customer value segmentation: VIP, regular, at-risk, lost."""
    if not customers:
        return {'total': 0, 'vip': [], 'at_risk': [], 'new_this_month': 0, 'recommendations': []}

    today = datetime.today().date()
    month_start = today.replace(day=1)

    # Map customer spend
    cust_spend = defaultdict(float)
    cust_last_sale = {}
    for s in sales:
        if s.customer_id:
            cust_spend[s.customer_id] += float(s.total_amount or 0)
            if s.customer_id not in cust_last_sale or s.created_at.date() > cust_last_sale[s.customer_id]:
                cust_last_sale[s.customer_id] = s.created_at.date()

    total_spend_vals = list(cust_spend.values())
    avg_spend = sum(total_spend_vals) / len(total_spend_vals) if total_spend_vals else 0

    vip, at_risk = [], []
    new_this_month = 0

    for c in customers:
        if c.created_at.date() >= month_start:
            new_this_month += 1

        spend = cust_spend.get(c.id, 0)
        last = cust_last_sale.get(c.id)
        days_since = (today - last).days if last else 9999

        if spend >= avg_spend * 1.5:
            vip.append({'name': c.name, 'spend': round(spend, 2), 'days_since': days_since})
        if days_since >= 60 and spend > 0:
            at_risk.append({'name': c.name, 'spend': round(spend, 2), 'days_since': days_since})

    recs = []
    if at_risk:
        recs.append(f'⚠️ {len(at_risk)} loyal customer(s) haven\'t bought in 60+ days. Send a re-engagement offer.')
    if vip:
        recs.append(f'🌟 {len(vip)} VIP customer(s) identified. Consider a loyalty reward program.')
    if new_this_month > 0:
        recs.append(f'🎉 {new_this_month} new customer(s) this month. Great acquisition momentum!')
    if not recs:
        recs.append('✅ Customer base is healthy.')

    return {
        'total': len(customers),
        'vip': vip[:5],
        'at_risk': at_risk[:5],
        'new_this_month': new_this_month,
        'recommendations': recs
    }


# ─────────────────────────────────────────────
# EXPENSE / ACCOUNTING AI
# ─────────────────────────────────────────────

def expense_insights(expenses):
    """Expense category breakdown, anomaly detection, budget warnings."""
    if not expenses:
        return {'total': 0, 'by_category': [], 'anomaly': [], 'recommendations': []}

    category_totals = defaultdict(float)
    monthly = defaultdict(float)

    for e in expenses:
        cat = getattr(e, 'category', None) or 'Uncategorized'
        if hasattr(cat, 'name'):
            cat = cat.name
        amount = float(e.amount or 0)
        category_totals[str(cat)] += amount
        month = e.created_at.strftime('%Y-%m')
        monthly[month] += amount

    by_category = sorted(
        [{'category': k, 'total': round(v, 2)} for k, v in category_totals.items()],
        key=lambda x: x['total'], reverse=True
    )

    # Anomaly: any month 50% higher than average
    month_vals = list(monthly.values())
    avg_month = sum(month_vals) / len(month_vals) if month_vals else 0
    anomaly = [
        {'month': k, 'amount': round(v, 2)}
        for k, v in monthly.items() if v > avg_month * 1.5
    ]

    recs = []
    if anomaly:
        recs.append(f'🚨 Unusual expense spike detected in {len(anomaly)} month(s). Review large transactions.')
    if by_category and by_category[0]['total'] > sum(v['total'] for v in by_category) * 0.6:
        recs.append(f'💡 "{by_category[0]["category"]}" dominates 60%+ of expenses. Consider cost reduction here.')
    if not recs:
        recs.append('✅ Expense distribution looks balanced.')

    return {
        'total': round(sum(category_totals.values()), 2),
        'by_category': by_category[:8],
        'anomaly': anomaly,
        'recommendations': recs
    }


# ─────────────────────────────────────────────
# HR / STAFF AI
# ─────────────────────────────────────────────

def hr_insights(staff_members):
    """Staff composition, salary analysis, active vs inactive."""
    if not staff_members:
        return {'total': 0, 'active': 0, 'payroll': 0, 'by_role': [], 'recommendations': []}

    active = [s for s in staff_members if s.is_active]
    payroll = sum(float(s.salary or 0) for s in active)
    role_count = defaultdict(int)
    for s in staff_members:
        role_count[s.role] += 1

    by_role = [{'role': k, 'count': v} for k, v in sorted(role_count.items(), key=lambda x: x[1], reverse=True)]

    recs = []
    inactive_count = len(staff_members) - len(active)
    if inactive_count > 0:
        recs.append(f'ℹ️ {inactive_count} inactive staff account(s). Review and deactivate if no longer needed.')
    if payroll > 50000:
        recs.append('💡 High monthly payroll. Review staff productivity metrics.')
    if len(active) < 2:
        recs.append('⚠️ Very small active team. Consider if staffing meets operational demand.')
    if not recs:
        recs.append('✅ Staff configuration looks healthy.')

    return {
        'total': len(staff_members),
        'active': len(active),
        'payroll': round(payroll, 2),
        'by_role': by_role,
        'recommendations': recs
    }


# ─────────────────────────────────────────────
# OVERALL BUSINESS HEALTH SCORE
# ─────────────────────────────────────────────

def business_health_score(sales_data, inventory_data, customer_data, expense_data):
    """Generate a 0–100 business health score with letter grade."""
    score = 70  # baseline

    # Sales
    if sales_data.get('trend') == 'up':
        score += 10
    elif sales_data.get('trend') == 'down':
        score -= 10

    # Inventory
    inv_score = inventory_data.get('score', 100)
    score += (inv_score - 70) * 0.2

    # Customers
    vip_count = len(customer_data.get('vip', []))
    at_risk_count = len(customer_data.get('at_risk', []))
    score += vip_count * 2 - at_risk_count * 3

    # Expenses
    anomalies = len(expense_data.get('anomaly', []))
    score -= anomalies * 5

    score = max(0, min(100, round(score)))

    if score >= 85:
        grade, color = 'A', '#10b981'
    elif score >= 70:
        grade, color = 'B', '#3b82f6'
    elif score >= 55:
        grade, color = 'C', '#f59e0b'
    else:
        grade, color = 'D', '#ef4444'

    return {'score': score, 'grade': grade, 'color': color}


# ─────────────────────────────────────────────
# INTERNAL HELPER
# ─────────────────────────────────────────────

def _slope(values):
    n = len(values)
    if n < 2:
        return 0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den != 0 else 0
