from app import create_app, db
from app.models import ChartAccount

app = create_app()
with app.app_context():
    # Find Dahabshil Bank accounts with code 1003
    accounts = ChartAccount.query.filter_by(account_code='1003', account_name='Dahabshil Bank').all()
    
    if accounts:
        # Update the first one
        acc = accounts[0]
        acc.account_code = '1002'
        acc.account_name = 'Amal Bank'
        db.session.commit()
        print(f"Updated account ID {acc.id} to Amal Bank (1002)")
    else:
        print("No Dahabshil Bank account with code 1003 found.")
