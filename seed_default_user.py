from app import create_app, db, bcrypt
from app.models import User, Tenant, Branch

def seed_data():
    app = create_app()
    with app.app_context():
        # Check if tenant exists
        tenant = Tenant.query.filter_by(name="Rays Technology Center").first()
        if not tenant:
            tenant = Tenant(
                name="Rays Technology Center",
                phone="0615123456",
                currency="$",
                slogan="Quality at its best"
            )
            db.session.add(tenant)
            db.session.flush()
            print(f"Created Tenant: {tenant.name}")

        # Check if user exists
        user = User.query.filter_by(email="raystechcenter@gmail.com").first()
        if not user:
            hashed_pw = bcrypt.generate_password_hash("rays1234").decode('utf-8')
            user = User(
                username="raystech",
                email="raystechcenter@gmail.com",
                password=hashed_pw,
                role='admin',
                tenant_id=tenant.id,
                is_active=True,
                is_super_admin=True
            )
            db.session.add(user)
            print(f"Created SuperAdmin User: {user.email} (Password: rays1234)")
        
        db.session.commit()
        
        # ── SEED CHART OF ACCOUNTS ──────────────────────────────────────────
        from app.models import ChartAccount
        
        standard_accounts = [
            # ASSETS
            {'code': '1000', 'name': 'Cash in Hand', 'category': 'ASSETS', 'sub': 'Bank Accounts'},
            {'code': '1010', 'name': 'Bank Account', 'category': 'ASSETS', 'sub': 'Bank Accounts'},
            {'code': '1020', 'name': 'EVC Plus', 'category': 'ASSETS', 'sub': 'Bank Accounts'},
            {'code': '1030', 'name': 'eDahab', 'category': 'ASSETS', 'sub': 'Bank Accounts'},
            {'code': '1100', 'name': 'Accounts Receivable', 'category': 'ASSETS', 'sub': 'Current Assets'},
            {'code': '1200', 'name': 'Inventory', 'category': 'ASSETS', 'sub': 'Current Assets'},
            {'code': '1500', 'name': 'Fixed Assets', 'category': 'ASSETS', 'sub': 'Non-Current Assets'},
            
            # LIABILITIES
            {'code': '2000', 'name': 'Accounts Payable', 'category': 'LIABILITIES', 'sub': 'Current Liabilities'},
            {'code': '2100', 'name': 'Sales Tax Payable', 'category': 'LIABILITIES', 'sub': 'Current Liabilities'},
            {'code': '2500', 'name': 'Long Term Loans', 'category': 'LIABILITIES', 'sub': 'Non-Current Liabilities'},
            
            # EQUITY
            {'code': '3000', 'name': "Owner's Equity", 'category': 'EQUITY', 'sub': 'Equity'},
            {'code': '3100', 'name': 'Retained Earnings', 'category': 'EQUITY', 'sub': 'Equity'},
            
            # REVENUE
            {'code': '4000', 'name': 'Sales Revenue', 'category': 'REVENUE', 'sub': 'Operating Revenue'},
            {'code': '4100', 'name': 'Service Revenue', 'category': 'REVENUE', 'sub': 'Operating Revenue'},
            {'code': '4500', 'name': 'Other Income', 'category': 'REVENUE', 'sub': 'Other Revenue'},
            
            # EXPENSES
            {'code': '5000', 'name': 'Cost of Goods Sold', 'category': 'EXPENSES', 'sub': 'Direct Expenses'},
            {'code': '5100', 'name': 'Salaries & Wages', 'category': 'EXPENSES', 'sub': 'Operating Expenses'},
            {'code': '5200', 'name': 'Rent Expense', 'category': 'EXPENSES', 'sub': 'Operating Expenses'},
            {'code': '5300', 'name': 'Utilities (Electricity/Water)', 'category': 'EXPENSES', 'sub': 'Operating Expenses'},
            {'code': '5400', 'name': 'Marketing & Advertising', 'category': 'EXPENSES', 'sub': 'Operating Expenses'},
            {'code': '5500', 'name': 'Office Supplies', 'category': 'EXPENSES', 'sub': 'Operating Expenses'},
            {'code': '5600', 'name': 'Maintenance & Repairs', 'category': 'EXPENSES', 'sub': 'Operating Expenses'},
        ]
        
        for acc in standard_accounts:
            existing_acc = ChartAccount.query.filter_by(account_code=acc['code'], tenant_id=tenant.id).first()
            if not existing_acc:
                new_acc = ChartAccount(
                    account_code=acc['code'],
                    account_name=acc['name'],
                    category=acc['category'],
                    sub_category=acc['sub'],
                    tenant_id=tenant.id,
                    is_active=True
                )
                db.session.add(new_acc)
                print(f"Added Account: {acc['name']} ({acc['code']})")
            else:
                # Update sub_category to ensure it shows in dropdowns
                existing_acc.sub_category = acc['sub']
                print(f"Updated Account: {acc['name']} ({acc['code']}) to sub-category: {acc['sub']}")
        
        db.session.commit()
        print(f"Chart of Accounts updated for {tenant.name}!")
    
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
