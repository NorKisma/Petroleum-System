import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        port=3307,
        database='rays_pos_db'
    )
    with connection.cursor() as cursor:
        columns = [
            "module_sales", "module_purchases", "module_customers", 
            "module_staff", "module_settings"
        ]
        tables = ["users", "tenants"]
        
        for table in tables:
            for col in columns:
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} BOOLEAN DEFAULT 1;")
                    print(f"Successfully added {col} to {table}")
                except Exception as e:
                    print(f"Skipping {col} on {table} (Might already exist): {e}")
        
    connection.commit()
    print("MySQL Migration successful!")
except Exception as e:
    print("Database connection failed:", e)
finally:
    if 'connection' in locals() and connection.open:
        connection.close()
