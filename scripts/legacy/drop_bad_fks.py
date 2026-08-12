from app import create_app, db
from sqlalchemy import text

def drop_bad_constraints():
    app = create_app()
    with app.app_context():
        print("Hagaajinta Foreign Keys ayaa bilaabatay...")
        
        # 1. Drop old FKs from share_investments
        try:
            db.session.execute(text("ALTER TABLE share_investments DROP FOREIGN KEY share_investments_ibfk_3"))
            print("- Foreign Key 'share_investments_ibfk_3' waa laga tirtiray share_investments.")
        except Exception as e:
            print(f"- share_investments DROP error: {str(e)}")

        # 2. Drop old FKs from share_withdrawals
        try:
            db.session.execute(text("ALTER TABLE share_withdrawals DROP FOREIGN KEY share_withdrawals_ibfk_3"))
            print("- Foreign Key 'share_withdrawals_ibfk_3' waa laga tirtiray share_withdrawals.")
        except Exception as e:
            print(f"- share_withdrawals DROP error: {str(e)}")
            
        db.session.commit()
        print("Guul! Database-ka waa la hagaajiyay.")

if __name__ == "__main__":
    drop_bad_constraints()
