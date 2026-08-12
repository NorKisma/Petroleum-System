from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    if 'customer_payments' in inspector.get_table_names():
        print("TABLE_EXISTS")
    else:
        print("TABLE_MISSING")
