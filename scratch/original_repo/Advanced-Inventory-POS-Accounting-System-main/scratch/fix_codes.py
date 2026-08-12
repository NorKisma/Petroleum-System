import os
from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    # Fix accounts with missing codes
    accounts_without_codes = ChartAccount.query.filter((ChartAccount.account_code == None) | (ChartAccount.account_code == '')).all()
    print(f"Found {len(accounts_without_codes)} accounts without codes.")
    
    ranges = {
        'ASSETS': (1000, 1999),
        'LIABILITIES': (2000, 2999),
        'EQUITY': (3000, 3999),
        'REVENUE': (4000, 4999),
        'EXPENSES': (5000, 5999)
    }
    
    for acc in accounts_without_codes:
        cat = acc.category
        if cat in ranges:
            start, end = ranges[cat]
            # Find next available code in this range
            existing_codes = [int(a.account_code) for a in ChartAccount.query.filter_by(category=cat).all() if a.account_code and a.account_code.isdigit()]
            next_code = max(existing_codes) + 1 if existing_codes else start
            if next_code < start: next_code = start
            
            acc.account_code = str(next_code)
            print(f"Assigned code {next_code} to {acc.account_name} ({cat})")
            
    db.session.commit()
    print("Database fix complete.")
