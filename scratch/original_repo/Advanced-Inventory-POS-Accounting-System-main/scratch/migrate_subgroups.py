from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    all_accounts = ChartAccount.query.all()
    
    for acc in all_accounts:
        if acc.category == 'ASSETS':
            name_lower = acc.account_name.lower()
            if any(k in name_lower for k in ['cash', 'bank', 'dahab', 'salaam', 'amal']):
                acc.sub_category = 'Cash & Bank'
            elif 'receivable' in name_lower:
                acc.sub_category = 'Accounts Receivable'
            elif 'inventory' in name_lower:
                acc.sub_category = 'Inventory'
            elif any(k in name_lower for k in ['land', 'building', 'vehicle', 'equipment', 'furniture']):
                acc.sub_category = 'Fixed Assets'
            else:
                acc.sub_category = 'Other Assets'
        elif acc.category == 'LIABILITIES':
            if 'payable' in acc.account_name.lower():
                acc.sub_category = 'Accounts Payable'
            else:
                acc.sub_category = 'Other Liabilities'
        
        print(f"Set Sub-Group '{acc.sub_category}' for account: {acc.account_name}")
    
    db.session.commit()
    print("Migration complete.")
