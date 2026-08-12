import sqlite3
import os

db_path = r'C:\Users\hp\OneDrive\Desktop\Advanced-Inventory-POS-Accounting-System\Advanced-Inventory-POS-Accounting-System\instance\pos_inventory.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ['users', 'tenants']
    columns = ['module_sales', 'module_purchases', 'module_customers', 'module_staff', 'module_settings']
    
    for table in tables:
        for col in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} BOOLEAN DEFAULT 1;")
                print(f"Added {col} to {table}")
            except sqlite3.OperationalError as e:
                print(f"Skipping {col} on {table}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration complete.")
else:
    print("DB not found at", db_path)
