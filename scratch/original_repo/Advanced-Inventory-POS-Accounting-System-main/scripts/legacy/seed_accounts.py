from app import create_app, db, bcrypt
from app.models import Tenant, User, ChartAccount

app = create_app()

DEFAULT_ACCOUNTS = [
    {'code': '1000', 'name': 'Cash on Hand', 'category': 'ASSETS', 'sub_category': 'Current Assets'},
    {'code': '1010', 'name': 'EVC Plus', 'category': 'ASSETS', 'sub_category': 'Bank Accounts'},
    {'code': '1020', 'name': 'eDahab', 'category': 'ASSETS', 'sub_category': 'Bank Accounts'},
    {'code': '1030', 'name': 'Premier Bank', 'category': 'ASSETS', 'sub_category': 'Bank Accounts'},
    {'code': '1040', 'name': 'Salaam Bank', 'category': 'ASSETS', 'sub_category': 'Bank Accounts'},
    {'code': '1100', 'name': 'Accounts Receivable', 'category': 'ASSETS', 'sub_category': 'Current Assets'},
    {'code': '1200', 'name': 'Inventory', 'category': 'ASSETS', 'sub_category': 'Current Assets'},
    {'code': '2000', 'name': 'Accounts Payable', 'category': 'LIABILITIES', 'sub_category': 'Current Liabilities'},
    {'code': '3000', 'name': 'Owner Equity', 'category': 'EQUITY', 'sub_category': 'Equity'},
    {'code': '4000', 'name': 'Sales Revenue', 'category': 'REVENUE', 'sub_category': 'Operating Revenue'},
    {'code': '5000', 'name': 'Cost of Goods Sold', 'category': 'EXPENSES', 'sub_category': 'Direct Costs'},
    {'code': '5100', 'name': 'General Expenses', 'category': 'EXPENSES', 'sub_category': 'Operating Expenses'},
    {'code': '5200', 'name': 'Salaries and Wages', 'category': 'EXPENSES', 'sub_category': 'Operating Expenses'}
]


with app.app_context():
    # 1. Create Default Tenant if none exist
    tenant = Tenant.query.first()
    if not tenant:
        print("No Tenant found. Creating default 'Rays Technology Center'...")
        tenant = Tenant(
            name="Rays Technology Center",
            phone="+252610000000",
            currency="$"
        )
        db.session.add(tenant)
        db.session.commit()
        
    # 2. Create Default Admin if none exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Creating default Admin user (admin@rays.com / admin123)...")
        hashed_pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
        admin = User(
            username="admin",
            email="admin@rays.com",
            password=hashed_pw,
            role="admin",
            tenant_id=tenant.id,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()

    # 3. Seed Accounts
    print(f"Seeding accounts for Tenant: {tenant.name}...")
    added = 0
    for acc in DEFAULT_ACCOUNTS:
        exists = ChartAccount.query.filter_by(tenant_id=tenant.id, account_code=acc['code']).first()
        if not exists:
            new_acc = ChartAccount(
                account_code=acc['code'],
                account_name=acc['name'],
                category=acc['category'],
                sub_category=acc['sub_category'],
                tenant_id=tenant.id
            )
            db.session.add(new_acc)
            added += 1
    
    db.session.commit()
    print(f"Added {added} new accounts for {tenant.name}.")
    print("\n[OK] Setup & Account Seeding Complete!")
