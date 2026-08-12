import sqlite3
import os

def fix_db():
    db_path = os.path.join('instance', 'pos.db')
    if not os.path.exists(db_path):
        db_path = 'pos.db' # fallback
        
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE purchase_items ADD COLUMN size TEXT")
        print("Added 'size' column to purchase_items")
    except sqlite3.OperationalError as e:
        print(f"purchase_items: {e}")
        
    try:
        cursor.execute("ALTER TABLE sale_items ADD COLUMN size TEXT")
        print("Added 'size' column to sale_items")
    except sqlite3.OperationalError as e:
        print(f"sale_items: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_db()
