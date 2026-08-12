"""
AI Sales Predictor — Rays Technology Center
Predicts future sales trends based on historical sales data.
Uses a simple moving average + linear trend model (no external ML library needed).
For advanced forecasting, swap in scikit-learn or Prophet.
"""

from datetime import datetime, timedelta
from collections import defaultdict


# ─── Core Prediction Engine ────────────────────────────────────────────────────

def _group_sales_by_day(sales):
    """Group sales list by date → {date_str: total_amount}."""
    daily = defaultdict(float)
    for sale in sales:
        day = sale.created_at.strftime("%Y-%m-%d")
        daily[day] += sale.total_amount
    return daily


def _moving_average(values, window=7):
    """Calculate simple moving average for a list of values."""
    if not values:
        return []
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        avg = sum(values[start:i + 1]) / (i - start + 1)
        result.append(round(avg, 2))
    return result


def _linear_trend(values):
    """
    Calculate linear trend slope using least squares.
    Returns (slope, intercept).
    """
    n = len(values)
    if n < 2:
        return 0, (values[0] if values else 0)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n
    numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean
    return slope, intercept


# ─── Public API ────────────────────────────────────────────────────────────────

def predict_next_days(sales, days_ahead=7, window=7):
    """
    Predict sales for the next `days_ahead` days.

    Args:
        sales: List of Sale model objects (must have .created_at, .total_amount)
        days_ahead: How many days into the future to forecast
        window: Moving average window size

    Returns:
        dict with keys:
          - 'historical': list of {date, amount} for past 30 days
          - 'predictions': list of {date, predicted_amount} for next N days
          - 'avg_daily':   float — average daily revenue
          - 'trend':       str — 'up' | 'down' | 'stable'
          - 'best_day':    str — day with highest predicted sales
    """
    daily = _group_sales_by_day(sales)

    # Build sorted list of last 30 days
    today = datetime.today().date()
    past_dates = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    historical_values = [daily.get(str(d), 0.0) for d in past_dates]

    ma = _moving_average(historical_values, window)
    slope, intercept = _linear_trend(historical_values)

    # Forecast
    predictions = []
    for i in range(1, days_ahead + 1):
        future_date = today + timedelta(days=i)
        predicted = intercept + slope * (len(historical_values) + i - 1)
        predicted = max(0, round(predicted, 2))  # no negative
        predictions.append({
            "date": str(future_date),
            "predicted_amount": predicted
        })

    # Trend analysis
    if slope > 5:
        trend = "up"
    elif slope < -5:
        trend = "down"
    else:
        trend = "stable"

    avg_daily = round(sum(historical_values) / len(historical_values), 2) if historical_values else 0

    best_day = max(predictions, key=lambda x: x["predicted_amount"])["date"] if predictions else None

    historical_out = [
        {"date": str(d), "amount": daily.get(str(d), 0.0)}
        for d in past_dates
    ]

    return {
        "historical": historical_out,
        "moving_average": [{"date": str(past_dates[i]), "avg": ma[i]} for i in range(len(past_dates))],
        "predictions": predictions,
        "avg_daily": avg_daily,
        "trend": trend,
        "best_day": best_day,
        "slope": round(slope, 4),
    }


def top_selling_products(sale_items, top_n=10):
    """
    Rank products by total quantity sold.

    Args:
        sale_items: List of SaleItem objects (must have .product, .quantity, .unit_price)
        top_n: How many top products to return

    Returns:
        list of dicts: {name, quantity, revenue}
    """
    product_data = defaultdict(lambda: {"quantity": 0, "revenue": 0.0})

    for item in sale_items:
        name = item.product.name if item.product else "Unknown"
        product_data[name]["quantity"] += item.quantity
        product_data[name]["revenue"] += item.quantity * item.unit_price

    sorted_products = sorted(
        [{"name": k, **v} for k, v in product_data.items()],
        key=lambda x: x["quantity"],
        reverse=True
    )
    return sorted_products[:top_n]


def slow_moving_products(products, threshold_days=30):
    """
    Identify products with no sales movement (potential dead stock).

    Args:
        products: List of Product objects
        threshold_days: Days with no movement = slow moving

    Returns:
        list of dicts: {name, stock_quantity, stock_value}
    """
    slow = []
    for p in products:
        # Simple heuristic: product has stock but no recent sales
        last_sold = None
        if p.sold_items:
            last_sold_item = max(p.sold_items, key=lambda si: si.sale.created_at)
            last_sold = last_sold_item.sale.created_at.date()

        days_since_sold = (datetime.today().date() - last_sold).days if last_sold else 9999

        if p.stock_quantity > 0 and days_since_sold >= threshold_days:
            slow.append({
                "name": p.name,
                "stock_quantity": p.stock_quantity,
                "stock_value": round(p.stock_quantity * p.buy_price, 2),
                "days_since_sold": days_since_sold if days_since_sold < 9999 else "Never sold"
            })

    return sorted(slow, key=lambda x: x["stock_quantity"], reverse=True)


def profit_margin_analysis(sale_items):
    """
    Calculate profit margin per product.

    Returns:
        list of dicts sorted by margin %: {name, revenue, cost, profit, margin_pct}
    """
    data = defaultdict(lambda: {"revenue": 0.0, "cost": 0.0, "quantity": 0})

    for item in sale_items:
        name = item.product.name if item.product else "Unknown"
        data[name]["revenue"] += item.quantity * item.unit_price
        data[name]["cost"] += item.quantity * item.buy_price
        data[name]["quantity"] += item.quantity

    result = []
    for name, d in data.items():
        profit = d["revenue"] - d["cost"]
        margin_pct = (profit / d["revenue"] * 100) if d["revenue"] > 0 else 0
        result.append({
            "name": name,
            "quantity": d["quantity"],
            "revenue": round(d["revenue"], 2),
            "cost": round(d["cost"], 2),
            "profit": round(profit, 2),
            "margin_pct": round(margin_pct, 1)
        })

    return sorted(result, key=lambda x: x["margin_pct"], reverse=True)
