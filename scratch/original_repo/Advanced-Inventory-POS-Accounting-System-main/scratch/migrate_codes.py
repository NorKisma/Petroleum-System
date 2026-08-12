from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    # Find accounts without codes
    accounts = ChartAccount.query.filter((ChartAccount.account_code == None) | (ChartAccount.account_code == '') | (ChartAccount.account_code == 'SYST')).all()
    
    for acc in accounts:
        # Determine base based on category and sub_category
        # Use simple defaults for migration
        base = 1000
        if acc.category == 'LIABILITIES': base = 2000
        elif acc.category == 'EQUITY': base = 3000
        elif acc.category == 'REVENUE': base = 4000
        elif acc.category == 'EXPENSES': base = 5000
        
        # Find next available code in this category
        last_acc = ChartAccount.query.filter_by(tenant_id=acc.tenant_id, category=acc.category)\
            .filter(ChartAccount.account_code.isnot(None))\
            .filter(ChartAccount.account_code != '')\
            .filter(ChartAccount.account_code != 'SYST')\
            .order_by(ChartAccount.account_code.desc()).first()
            
        if last_acc and last_acc.account_code.isdigit():
            next_code = int(last_acc.account_code) + 1
        else:
            next_code = base + 1
            
        acc.account_code = str(next_code)
        print(f"Assigned code {acc.account_code} to account: {acc.account_name}")
    
    db.session.commit()
    print("Migration complete.")
