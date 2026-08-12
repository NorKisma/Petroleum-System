import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    port=3307,
    database='rays_pos_db'
)

try:
    with conn.cursor() as cursor:
        cursor.execute("DESCRIBE tenants")
        cols = [c[0] for c in cursor.fetchall()]
        
        # 1. Handle the staff -> hrm rename
        if 'module_staff' in cols and 'module_hrm' not in cols:
            cursor.execute("ALTER TABLE tenants CHANGE module_staff module_hrm BOOLEAN DEFAULT TRUE")
            print("Renamed module_staff to module_hrm")
        
        # 2. Add all missing modules if they don't exist
        new_cols = [
            ("module_hrm", "BOOLEAN DEFAULT TRUE"),
            ("module_add_sale", "BOOLEAN DEFAULT TRUE"),
            ("module_tables", "BOOLEAN DEFAULT FALSE"),
            ("module_modifiers", "BOOLEAN DEFAULT FALSE"),
            ("module_kitchen", "BOOLEAN DEFAULT FALSE"),
            ("module_subscription", "BOOLEAN DEFAULT FALSE"),
            ("module_types_of_service", "BOOLEAN DEFAULT FALSE")
        ]
        
        for col_name, col_type in new_cols:
            if col_name not in cols:
                try:
                    cursor.execute(f"ALTER TABLE tenants ADD COLUMN {col_name} {col_type}")
                    print(f"Added column: {col_name}")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")
        
    conn.commit()
finally:
    conn.close()
