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
        # Get all columns in tenants table
        cursor.execute("DESCRIBE tenants")
        cols = [c[0] for c in cursor.fetchall()]
        
        # Identify all module columns
        module_cols = [col for col in cols if col.startswith('module_')]
        
        if not module_cols:
            print("No module columns found.")
        else:
            # Build update query
            set_clause = ", ".join([f"{col} = 1" for col in module_cols])
            update_query = f"UPDATE tenants SET {set_clause}"
            
            cursor.execute(update_query)
            print(f"Enabled {len(module_cols)} modules for all tenants.")
            print(f"Modules: {', '.join(module_cols)}")
            
    conn.commit()
finally:
    conn.close()
