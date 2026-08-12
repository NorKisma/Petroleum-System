"""
reset_and_seed.py — Reset all data and create default admin user
Run: python reset_and_seed.py
"""
import sys
import io
from datetime import datetime, timedelta
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db, bcrypt
from app.models import (
    Tenant, User, Category, Product, Customer, Vendor,
    Purchase, PurchaseItem, Sale, SaleItem, SaleReturn, SaleReturnItem,
    PurchaseReturn, PurchaseReturnItem, Expense, OtherIncome,
    CustomerPayment, VendorPayment, Shareholder, ShareInvestment,
    ShareWithdrawal, Asset, BankAccount, BankTransfer, AuditLog, ChartAccount, Branch
)

app = create_app()

with app.app_context():
    print("\n[!] Recreating Database Schema (Drop & Create)...")
    db.drop_all()
    db.create_all()
    print("[OK] All tables recreated successfully.")

    # ── Create Default Tenant ─────────────────────────────────────────────────
    tenant = Tenant(
        name="Rays Technology Center",
        phone="+252612345678",
        email="raystechcenter@gmail.com",
        address="Mogadishu, Somalia",
        slogan="Powering Business with Technology",
        currency="$",
        tax_rate=0.0,
        subscription_plan="pro",
        subscription_status="active",
        subscription_expiry=datetime.utcnow() + timedelta(days=365)
    )
    db.session.add(tenant)
    db.session.flush()
    print(f"[OK] Tenant created: {tenant.name} (ID: {tenant.id})")

    # ── Create Default Branch ─────────────────────────────────────────────────
    branch = Branch(
        name="Main Branch - Mogadishu",
        location="Waberi District",
        phone="+252612345678",
        tenant_id=tenant.id
    )
    db.session.add(branch)
    db.session.flush()
    print(f"[OK] Branch created: {branch.name}")

    # ── Create Standard Chart of Accounts ─────────────────────────────────────
    accounts = [
        {'code': '1001', 'name': 'Cash', 'cat': 'ASSETS', 'sub': 'Current Assets'},
        {'code': '1002', 'name': 'Inventory', 'cat': 'ASSETS', 'sub': 'Current Assets'},
        {'code': '2001', 'name': 'Accounts Payable', 'cat': 'LIABILITIES', 'sub': 'Current Liabilities'},
        {'code': '3001', 'name': 'Owner Capital', 'cat': 'EQUITY', 'sub': 'Equity'},
        {'code': '4001', 'name': 'Sales Revenue', 'cat': 'REVENUE', 'sub': 'Operating Revenue'},
        {'code': '5001', 'name': 'Cost of Goods Sold', 'cat': 'EXPENSES', 'sub': 'Direct Costs'},
        {'code': '6001', 'name': 'General Expenses', 'cat': 'EXPENSES', 'sub': 'Operating Expenses'},
    ]
    for acc in accounts:
        chart_acc = ChartAccount(
            account_code=acc['code'],
            account_name=acc['name'],
            category=acc['cat'],
            sub_category=acc['sub'],
            tenant_id=tenant.id
        )
        db.session.add(chart_acc)
    print("[OK] Standard Chart of Accounts seeded.")

    # ── Create Default Admin User ─────────────────────────────────────────────
    hashed_pw = bcrypt.generate_password_hash("Rays123").decode("utf-8")
    admin = User(
        username="admin",
        email="raystechcenter@gmail.com",
        password=hashed_pw,
        role="developer",
        tenant_id=tenant.id,
        branch_id=branch.id,
        is_active=True,
        is_super_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    print(f"[OK] Admin user created: {admin.username}")
    print("--------------------------------------------------")
    print("Setup Complete! You can now login with:")
    print("Email: raystechcenter@gmail.com | Password: Rays123")
    print("--------------------------------------------------")
    print("  Role     : Admin")
    print("  Business : Rays Technology Center")
    print("=" * 45)
    print("")
    print("[DONE] System is ready! Run: python run.py")
    print("")
