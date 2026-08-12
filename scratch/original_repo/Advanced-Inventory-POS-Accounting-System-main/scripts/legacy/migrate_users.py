"""
migrate_users.py — Universal Migration Script
Works with both SQLite and MySQL/PostgreSQL.
Run once: python migrate_users.py
"""

import sys
from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

with app.app_context():
    # -- Detect Database Type ---------------------------------------------------
    dialect = db.engine.dialect.name  # 'sqlite', 'mysql', 'postgresql'
    print(f"INFO: Database dialect detected -> {dialect.upper()}")

    # -- Helper: check if column exists ----------------------------------------
    def column_exists(table_name, column_name):
        inspector = inspect(db.engine)
        cols = [c['name'] for c in inspector.get_columns(table_name)]
        return column_name in cols

    # -- Migration Tasks --------------------------------------------------------
    migrations = [
        {
            'description': "Add 'created_at' to users table",
            'table':  'users',
            'column': 'created_at',
            'sqlite_sql':  "ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP",
            'mysql_sql':   "ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT NOW()",
            'pg_sql':      "ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW()",
        },
        {
            'description': "Add 'is_active' to users table",
            'table':  'users',
            'column': 'is_active',
            'sqlite_sql':  "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1",
            'mysql_sql':   "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE",
            'pg_sql':      "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE",
        },
        {
            'description': "Add 'slogan' to tenants table",
            'table':  'tenants',
            'column': 'slogan',
            'sqlite_sql':  "ALTER TABLE tenants ADD COLUMN slogan VARCHAR(255)",
            'mysql_sql':   "ALTER TABLE tenants ADD COLUMN slogan VARCHAR(255)",
            'pg_sql':      "ALTER TABLE tenants ADD COLUMN slogan VARCHAR(255)",
        },
        {
            'description': "Add 'otp_code' to users table",
            'table':  'users',
            'column': 'otp_code',
            'sqlite_sql':  "ALTER TABLE users ADD COLUMN otp_code VARCHAR(10)",
            'mysql_sql':   "ALTER TABLE users ADD COLUMN otp_code VARCHAR(10)",
            'pg_sql':      "ALTER TABLE users ADD COLUMN otp_code VARCHAR(10)",
        },
        {
            'description': "Add 'otp_expiry' to users table",
            'table':  'users',
            'column': 'otp_expiry',
            'sqlite_sql':  "ALTER TABLE users ADD COLUMN otp_expiry DATETIME",
            'mysql_sql':   "ALTER TABLE users ADD COLUMN otp_expiry DATETIME",
            'pg_sql':      "ALTER TABLE users ADD COLUMN otp_expiry TIMESTAMP",
        },
        {
            'description': "Add 'monthly_fee' to tenants table",
            'table':  'tenants',
            'column': 'monthly_fee',
            'sqlite_sql':  "ALTER TABLE tenants ADD COLUMN monthly_fee FLOAT DEFAULT 15.0",
            'mysql_sql':   "ALTER TABLE tenants ADD COLUMN monthly_fee FLOAT DEFAULT 15.0",
            'pg_sql':      "ALTER TABLE tenants ADD COLUMN monthly_fee FLOAT DEFAULT 15.0",
        },
        {
            'description': "Add 'subscription_status' to tenants table",
            'table':  'tenants',
            'column': 'subscription_status',
            'sqlite_sql':  "ALTER TABLE tenants ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'Unpaid'",
            'mysql_sql':   "ALTER TABLE tenants ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'Unpaid'",
            'pg_sql':      "ALTER TABLE tenants ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'Unpaid'",
        },
        {
            'description': "Add 'last_payment_date' to tenants table",
            'table':  'tenants',
            'column': 'last_payment_date',
            'sqlite_sql':  "ALTER TABLE tenants ADD COLUMN last_payment_date DATETIME",
            'mysql_sql':   "ALTER TABLE tenants ADD COLUMN last_payment_date DATETIME",
            'pg_sql':      "ALTER TABLE tenants ADD COLUMN last_payment_date TIMESTAMP",
        },
        {
            'description': "Add 'subscription_balance' to tenants table",
            'table':  'tenants',
            'column': 'subscription_balance',
            'sqlite_sql':  "ALTER TABLE tenants ADD COLUMN subscription_balance FLOAT DEFAULT 15.0",
            'mysql_sql':   "ALTER TABLE tenants ADD COLUMN subscription_balance FLOAT DEFAULT 15.0",
            'pg_sql':      "ALTER TABLE tenants ADD COLUMN subscription_balance FLOAT DEFAULT 15.0",
        },
    ]

    success = 0
    skipped = 0
    failed  = 0

    print("\n-- Running Migrations ----------------------------------------")

    for m in migrations:
        desc   = m['description']
        table  = m['table']
        column = m['column']

        # Check if column already exists
        if column_exists(table, column):
            print(f"  SKIP   [{desc}] — column already exists")
            skipped += 1
            continue

        # Choose correct SQL for this dialect
        if dialect == 'sqlite':
            sql = m['sqlite_sql']
        elif dialect == 'mysql':
            sql = m['mysql_sql']
        elif dialect in ('postgresql', 'postgres'):
            sql = m['pg_sql']
        else:
            sql = m['mysql_sql']  # fallback

        try:
            with db.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            print(f"  OK     [{desc}]")
            success += 1
        except Exception as e:
            print(f"  FAIL   [{desc}] → {e}")
            failed += 1

    print("-------------------------------------------------------------")
    print(f"  Done: {success} applied, {skipped} skipped, {failed} failed\n")

    if failed > 0:
        sys.exit(1)
