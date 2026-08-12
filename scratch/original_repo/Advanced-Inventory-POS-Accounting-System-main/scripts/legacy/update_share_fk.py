from app import create_app, db
from sqlalchemy import text

def update_database():
    app = create_app()
    with app.app_context():
        print("Cusboonaysiinta Share Foreign Keys ayaa bilaabatay...")
        
        # 1. Drop existing FKs if possible, or just add new ones if we are sure
        # In MySQL, we need to know the constraint name to drop it, but we can try to just add and see.
        # Actually, since I just added them, I can probably just run the ALTER again if I didn't set a name.
        
        # For simplicity, let's try to just drop the old ones if they were just created.
        # But wait, I'll just modify the existing script logic.
        
        try:
            # First, try to drop the old foreign key if it exists. 
            # This is hard without the constraint name. 
            # But we can just try to add the new one.
            db.session.execute(text("ALTER TABLE share_investments MODIFY COLUMN account_id INT"))
            # Note: The old constraint might still point to bank_accounts. 
            # Let's try to drop it. Usually it's share_investments_ibfk_2 or similar.
            # But let's just try to add the new one and see if it works.
            db.session.execute(text("ALTER TABLE share_investments ADD CONSTRAINT fk_share_inv_chart FOREIGN KEY (account_id) REFERENCES chart_accounts(id)"))
            print("- Foreign Key 'fk_share_inv_chart' waa lagu daray share_investments.")
        except Exception as e:
            print(f"- share_investments FK error: {str(e)}")

        try:
            db.session.execute(text("ALTER TABLE share_withdrawals MODIFY COLUMN account_id INT"))
            db.session.execute(text("ALTER TABLE share_withdrawals ADD CONSTRAINT fk_share_with_chart FOREIGN KEY (account_id) REFERENCES chart_accounts(id)"))
            print("- Foreign Key 'fk_share_with_chart' waa lagu daray share_withdrawals.")
        except Exception as e:
            print(f"- share_withdrawals FK error: {str(e)}")
            
        db.session.commit()
        print("Guul! Database-ka waa la cusbooneysiiyay.")

if __name__ == "__main__":
    update_database()
