import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from app.models import FuelDelivery
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 1. Alter existing table to add paid_amount
    try:
        db.session.execute(text("ALTER TABLE fuel_deliveries ADD COLUMN paid_amount FLOAT DEFAULT 0.0;"))
        db.session.commit()
        print("Column paid_amount added successfully.")
    except Exception as e:
        print("Failed to add column (it might already exist):", e)
        db.session.rollback()

    # 2. Create the new fuel_delivery_payments table (db.create_all will handle this safely)
    db.create_all()
    print("Ensured all new tables are created.")

    # 3. Backfill existing deliveries
    try:
        deliveries = FuelDelivery.query.all()
        count = 0
        for d in deliveries:
            if d.payment_method == 'CASH' and (d.paid_amount is None or d.paid_amount == 0.0):
                d.paid_amount = d.total_cost
                count += 1
        db.session.commit()
        print(f"Backfilled {count} existing CASH deliveries.")
    except Exception as e:
        print("Failed to backfill data:", e)
        db.session.rollback()
