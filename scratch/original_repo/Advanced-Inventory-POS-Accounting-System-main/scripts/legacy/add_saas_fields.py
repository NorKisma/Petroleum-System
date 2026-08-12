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
        
        new_cols = [
            ("default_sale_discount", "FLOAT DEFAULT 0.0"),
            ("default_sale_tax", "VARCHAR(50) NULL"),
            ("sales_item_addition_method", "VARCHAR(50) DEFAULT 'add_new'"),
            ("amount_rounding_method", "VARCHAR(50) DEFAULT 'none'"),
            ("sales_price_is_minimum", "BOOLEAN DEFAULT FALSE"),
            ("allow_overselling", "BOOLEAN DEFAULT FALSE"),
            ("enable_sales_order", "BOOLEAN DEFAULT FALSE"),
            ("is_pay_term_required", "BOOLEAN DEFAULT FALSE"),
            ("sales_commission_agent", "VARCHAR(50) DEFAULT 'disable'"),
            ("commission_calculation_type", "VARCHAR(50) DEFAULT 'percentage'"),
            ("is_commission_agent_required", "BOOLEAN DEFAULT FALSE"),
            ("enable_payment_link", "BOOLEAN DEFAULT FALSE"),
            ("razorpay_key_id", "VARCHAR(255) NULL"),
            ("razorpay_key_secret", "VARCHAR(255) NULL"),
            ("stripe_public_key", "VARCHAR(255) NULL"),
            ("stripe_secret_key", "VARCHAR(255) NULL")
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
