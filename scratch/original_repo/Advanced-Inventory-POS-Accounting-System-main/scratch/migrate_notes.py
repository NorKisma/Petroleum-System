from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text('ALTER TABLE chart_accounts ADD COLUMN notes TEXT'))
        db.session.commit()
        print("Column 'notes' added successfully.")
    except Exception as e:
        print(f"Error or column already exists: {e}")
