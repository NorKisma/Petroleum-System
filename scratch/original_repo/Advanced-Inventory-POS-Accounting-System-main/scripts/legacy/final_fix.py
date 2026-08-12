from app import create_app, db
from app.models import Tenant, User, Product, Sale, SaleItem, AuditLog, Expense

app = create_app()

with app.app_context():
    try:
        print("--- Final Syncing ---")
        # Direct creation from models
        db.create_all()
        print("Success: Database Tables created effectively.")
        
        # Test if users table exists by selecting count
        user_count = User.query.count()
        print(f"Current users in DB: {user_count}")
        
    except Exception as e:
        print(f"Fatal Setup Error: {e}")
