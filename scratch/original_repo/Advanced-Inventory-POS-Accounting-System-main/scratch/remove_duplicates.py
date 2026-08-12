from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    # Find all active accounts for the first tenant (assuming current_user's tenant is 1 or similar)
    # Actually, let's do it for all tenants or just the active one.
    # The user screenshot shows many duplicates.
    
    accounts = ChartAccount.query.filter_by(is_active=True).all()
    seen_names = {}
    to_delete = []
    
    for a in accounts:
        key = (a.tenant_id, a.account_name.lower().strip())
        if key in seen_names:
            # Duplicate found. Keep the one with the "prettier" code or the one already seen?
            # Standard codes: 1000, 1010, 1020, 2000, 3000, 4000, 5000.
            standard_codes = ['1000', '1010', '1020', '1030', '2000', '3000', '4000', '5000']
            if a.account_code in standard_codes:
                # Keep this one, delete the previous one
                to_delete.append(seen_names[key])
                seen_names[key] = a
            else:
                # Keep the previous one, delete this one
                to_delete.append(a)
        else:
            seen_names[key] = a
            
    for a in to_delete:
        print(f"Deleting duplicate: {a.account_name} (Code: {a.account_code})")
        # Soft delete or hard delete? User said "ka saar" (remove).
        db.session.delete(a)
        
    db.session.commit()
    print(f"Removed {len(to_delete)} duplicate accounts.")
