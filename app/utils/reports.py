"""
PDF & Excel Report Generator Utility
Generates printable PDF reports for sales, expenses, inventory, and financial statements.
Uses only built-in Python + minimal dependencies (no weasyprint/reportlab needed).
Produces an HTML-based printable page returned as a Flask response.
"""

from flask import make_response, render_template_string
from datetime import datetime


# ─── HTML Print Template ───────────────────────────────────────────────────────
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{{ title }}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: Arial, sans-serif; font-size: 12px; color: #222; padding: 20px; }
  h1  { font-size: 20px; margin-bottom: 4px; }
  h3  { font-size: 13px; color: #555; margin-bottom: 16px; }
  table { width: 100%; border-collapse: collapse; margin-top: 10px; }
  th { background: #1e3a5f; color: #fff; padding: 8px 6px; text-align: left; font-size: 11px; }
  td { padding: 7px 6px; border-bottom: 1px solid #e0e0e0; }
  tr:nth-child(even) { background: #f5f8ff; }
  .total-row td { font-weight: bold; background: #eaf0fb; border-top: 2px solid #1e3a5f; }
  .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
  .generated { font-size: 10px; color: #888; }
  @media print {
    body { padding: 0; }
    .no-print { display: none; }
  }
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>{{ business_name }}</h1>
      <h3>{{ title }}</h3>
    </div>
    <div class="generated">Generated: {{ generated_at }}<br>Period: {{ period }}</div>
  </div>

  <table>
    <thead>
      <tr>{% for col in columns %}<th>{{ col }}</th>{% endfor %}</tr>
    </thead>
    <tbody>
      {% for row in rows %}
      <tr>{% for cell in row %}<td>{{ cell }}</td>{% endfor %}</tr>
      {% endfor %}
      {% if totals %}
      <tr class="total-row">{% for cell in totals %}<td>{{ cell }}</td>{% endfor %}</tr>
      {% endif %}
    </tbody>
  </table>

  <br>
  <button class="no-print" onclick="window.print()" 
    style="padding:10px 24px;background:#1e3a5f;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px;">
    🖨️ Print / Save PDF
  </button>
</body>
</html>
"""


def _render_report(title, columns, rows, totals=None, business_name="Rays Technology Center", period="All Time"):
    """Render an HTML report page that the browser can print as PDF."""
    html = render_template_string(
        REPORT_TEMPLATE,
        title=title,
        columns=columns,
        rows=rows,
        totals=totals or [],
        business_name=business_name,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        period=period
    )
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"
    return response


# ─── Public Report Functions ───────────────────────────────────────────────────

def generate_sales_report(sales, business_name="Rays Technology Center", period="All Time"):
    """Generate a printable sales report."""
    columns = ["#", "Invoice No", "Customer", "Payment", "Amount", "Date"]
    rows = []
    total = 0
    for i, s in enumerate(sales, 1):
        customer = s.customer.name if s.customer else "Walk-in"
        rows.append([
            i,
            s.invoice_no,
            customer,
            s.payment_method,
            f"${s.total_amount:,.2f}",
            s.created_at.strftime("%Y-%m-%d")
        ])
        total += s.total_amount
    totals = ["", "", "", "TOTAL", f"${total:,.2f}", ""]
    return _render_report("Sales Report", columns, rows, totals, business_name, period)


def generate_expenses_report(expenses, business_name="Rays Technology Center", period="All Time"):
    """Generate a printable expenses report."""
    columns = ["#", "Description", "Category", "Amount", "Date"]
    rows = []
    total = 0
    for i, e in enumerate(expenses, 1):
        rows.append([
            i,
            e.description,
            e.category,
            f"${e.amount:,.2f}",
            e.created_at.strftime("%Y-%m-%d")
        ])
        total += e.amount
    totals = ["", "", "TOTAL", f"${total:,.2f}", ""]
    return _render_report("Expenses Report", columns, rows, totals, business_name, period)


def generate_inventory_report(products, business_name="Rays Technology Center"):
    """Generate a printable inventory / stock report."""
    columns = ["#", "Product", "Category", "Buy Price", "Sell Price", "Stock", "Stock Value"]
    rows = []
    total_value = 0
    for i, p in enumerate(products, 1):
        cat = p.category.name if p.category else "—"
        value = p.stock_quantity * p.buy_price
        rows.append([
            i,
            p.name,
            cat,
            f"${p.buy_price:,.2f}",
            f"${p.sell_price:,.2f}",
            p.stock_quantity,
            f"${value:,.2f}"
        ])
        total_value += value
    totals = ["", "", "", "", "", "TOTAL VALUE", f"${total_value:,.2f}"]
    return _render_report("Inventory Report", columns, rows, totals, business_name)


def generate_financial_report(data, business_name="Rays Technology Center", period="All Time"):
    """
    Generate a printable Profit & Loss / Financial Report.
    data: dict with keys: total_revenue, total_cogs, gross_profit,
          total_expenses, total_other_income, net_profit
    """
    columns = ["Item", "Amount"]
    rows = [
        ["Sales Revenue",       f"${data.get('total_revenue', 0):,.2f}"],
        ["Cost of Goods Sold",  f"(${data.get('total_cogs', 0):,.2f})"],
        ["Gross Profit",        f"${data.get('gross_profit', 0):,.2f}"],
        ["Other Income",        f"${data.get('total_other_income', 0):,.2f}"],
        ["Operating Expenses",  f"(${data.get('total_expenses', 0):,.2f})"],
    ]
    net = data.get('net_profit', 0)
    totals = ["Net Profit / (Loss)", f"${net:,.2f}"]
    return _render_report("Financial Report (P&L)", columns, rows, totals, business_name, period)


def generate_balance_sheet_report(data, business_name="Rays Technology Center"):
    """Generate a printable Balance Sheet."""
    columns = ["Account", "Amount"]
    rows = [
        ["── ASSETS ──",              ""],
        ["Bank / Cash",               f"${data.get('total_bank_balance', 0):,.2f}"],
        ["Accounts Receivable (AR)",  f"${data.get('receivables', 0):,.2f}"],
        ["Inventory",                 f"${data.get('inventory_value', 0):,.2f}"],
        ["Fixed Assets",              f"${data.get('other_assets_value', 0):,.2f}"],
        ["",                          ""],
        ["── LIABILITIES ──",         ""],
        ["Accounts Payable (AP)",     f"${data.get('payables', 0):,.2f}"],
        ["",                          ""],
        ["── EQUITY ──",              ""],
        ["Shareholder Capital",       f"${data.get('equity_capital', 0):,.2f}"],
        ["Retained Earnings (Net P)", f"${data.get('net_profit', 0):,.2f}"],
    ]
    totals = ["Total Assets", f"${data.get('total_assets', 0):,.2f}"]
    return _render_report("Balance Sheet", columns, rows, totals, business_name)

def generate_cash_flow_report(data, business_name="Rays Technology Center"):
    """Generate a printable Cash Flow Statement."""
    columns = ["Category", "Amount"]
    rows = [
        ["── OPERATING ACTIVITIES ──", ""],
        ["  + Cash Sales", f"${data.get('cash_sales', 0):,.2f}"],
        ["  + Customer Payments", f"${data.get('customer_payments', 0):,.2f}"],
        ["  + Other Income", f"${data.get('other_income', 0):,.2f}"],
        ["  - Cash Purchases", f"(${data.get('cash_purchases', 0):,.2f})"],
        ["  - Vendor Payments", f"(${data.get('vendor_payments', 0):,.2f})"],
        ["  - Expenses", f"(${data.get('expenses', 0):,.2f})"],
        ["Net Cash from Operating Activities", f"${data.get('net_operating_cash', 0):,.2f}"],
        ["", ""],
        ["── INVESTING ACTIVITIES ──", ""],
        ["  - Asset Purchases", f"(${data.get('asset_purchases', 0):,.2f})"],
        ["Net Cash from Investing Activities", f"${data.get('net_investing_cash', 0):,.2f}"],
        ["", ""],
        ["── FINANCING ACTIVITIES ──", ""],
        ["  + Shareholder Investments", f"${data.get('share_investments', 0):,.2f}"],
        ["  - Shareholder Withdrawals", f"(${data.get('share_withdrawals', 0):,.2f})"],
        ["Net Cash from Financing Activities", f"${data.get('net_financing_cash', 0):,.2f}"]
    ]
    totals = ["Net Cash Flow", f"${data.get('net_cash_flow', 0):,.2f}"]
    return _render_report("Cash Flow Statement", columns, rows, totals, business_name)
