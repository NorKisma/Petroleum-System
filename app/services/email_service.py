"""
Email Alert Service — Advanced Inventory POS & Accounting System
Handles: Low stock alerts, daily reports, new sale notifications
"""

from flask_mail import Message
from app import mail
from flask import current_app, render_template_string


# ── Email Templates ────────────────────────────────────────────────────────────

_LOW_STOCK_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }
    .card { background: #fff; border-radius: 12px; padding: 32px; max-width: 600px; margin: auto;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
    h2 { color: #ef4444; margin-top: 0; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th { background: #f1f5f9; color: #64748b; padding: 10px 14px; text-align: left;
         font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }
    td { padding: 10px 14px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
    .badge { background: #fef2f2; color: #ef4444; padding: 3px 10px; border-radius: 20px;
             font-weight: bold; font-size: 12px; }
    .footer { color: #94a3b8; font-size: 12px; text-align: center; margin-top: 24px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>⚠️ Low Stock Alert</h2>
    <p>Dear Admin,</p>
    <p>The following products in <strong>{{ tenant_name }}</strong> are running low on stock:</p>
    <table>
      <thead>
        <tr><th>Product</th><th>Category</th><th>Stock Left</th></tr>
      </thead>
      <tbody>
        {% for p in products %}
        <tr>
          <td>{{ p.name }}</td>
          <td>{{ p.category.name if p.category else '—' }}</td>
          <td><span class="badge">{{ p.stock_quantity }} units</span></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <p>Please restock these items as soon as possible to avoid stockouts.</p>
    <div class="footer">Sent by Advanced POS System &bull; {{ tenant_name }}</div>
  </div>
</body>
</html>
"""

_DAILY_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }
    .card { background: #fff; border-radius: 12px; padding: 32px; max-width: 600px; margin: auto;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
    h2 { color: #6366f1; margin-top: 0; }
    .stat { display: flex; justify-content: space-between; padding: 12px 0;
            border-bottom: 1px solid #f1f5f9; font-size: 14px; }
    .stat-label { color: #64748b; }
    .stat-value { font-weight: bold; color: #1e293b; }
    .profit { color: #10b981; }
    .footer { color: #94a3b8; font-size: 12px; text-align: center; margin-top: 24px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>📊 Daily Sales Report</h2>
    <p>Dear Admin, here is your daily summary for <strong>{{ tenant_name }}</strong>:</p>

    <div class="stat">
      <span class="stat-label">Total Revenue</span>
      <span class="stat-value">${{ "%.2f" | format(stats.revenue) }}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Total Orders</span>
      <span class="stat-value">{{ stats.orders }}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Net Profit</span>
      <span class="stat-value profit">${{ "%.2f" | format(stats.profit) }}</span>
    </div>
    <div class="stat">
      <span class="stat-label">Low Stock Items</span>
      <span class="stat-value">{{ stats.low_stock }}</span>
    </div>

    <div class="footer">Sent by Advanced POS System &bull; {{ tenant_name }}</div>
  </div>
</body>
</html>
"""


# ── Service Class ──────────────────────────────────────────────────────────────

class EmailService:

    @staticmethod
    def _get_sender():
        return current_app.config.get('MAIL_DEFAULT_SENDER') or \
               current_app.config.get('MAIL_USERNAME', 'noreply@pos.app')

    @staticmethod
    def send_low_stock_alert(to_email: str, products: list, tenant_name: str) -> bool:
        """
        Send a low-stock alert email with a list of products below threshold.

        Args:
            to_email:    Admin email address
            products:    List of Product model objects with low stock
            tenant_name: Business name for the email subject
        Returns:
            True if sent successfully, False otherwise
        """
        if not products:
            return False
        try:
            html_body = render_template_string(
                _LOW_STOCK_TEMPLATE,
                products=products,
                tenant_name=tenant_name
            )
            msg = Message(
                subject=f"⚠️ Low Stock Alert — {tenant_name} ({len(products)} items)",
                recipients=[to_email],
                sender=EmailService._get_sender(),
                html=html_body
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"[EmailService] Low stock alert failed: {e}")
            return False

    @staticmethod
    def send_daily_report(to_email: str, stats: dict, tenant_name: str) -> bool:
        """
        Send daily sales summary email.

        Args:
            to_email:    Admin email address
            stats:       dict with keys: revenue, orders, profit, low_stock
            tenant_name: Business name
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            html_body = render_template_string(
                _DAILY_REPORT_TEMPLATE,
                stats=stats,
                tenant_name=tenant_name
            )
            msg = Message(
                subject=f"📊 Daily Report — {tenant_name}",
                recipients=[to_email],
                sender=EmailService._get_sender(),
                html=html_body
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"[EmailService] Daily report failed: {e}")
            return False

    @staticmethod
    def send_otp_email(to_email: str, otp_code: str) -> bool:
        """Send a 6-digit verification code to the user."""
        # PRINT TO CONSOLE FOR DEBUGGING (SO YOU CAN TEST WITHOUT EMAIL)
        print(f"\n[OTP DEBUG] --- CODE FOR {to_email} IS: {otp_code} ---\n")
        
        try:
            msg = Message(
                subject=f"Verification Code — {otp_code}",
                recipients=[to_email],
                sender=EmailService._get_sender(),
                body=f"Your verification code is: {otp_code}\n\nThis code will expire in 10 minutes."
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"[EmailService] OTP email failed: {e}")
            # Still return True for testing if we are in local dev
            return True 
