"""
╔══════════════════════════════════════════════════════════╗
║     Rays POS — MySQL Database Setup & Migration Script   ║
║     Run this once to create the MySQL database           ║
╚══════════════════════════════════════════════════════════╝

Usage:
    python setup_mysql.py

Requirements:
    - XAMPP MySQL must be running (Start MySQL in XAMPP Control Panel)
    - PyMySQL must be installed: pip install pymysql
"""

import pymysql
import sys

# ── Configuration ─────────────────────────────────────────────────────────────
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3307
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''          # XAMPP default = no password
DB_NAME = 'rays_pos_db'
CHARSET = 'utf8mb4'

def banner(msg):
    print(f"\n{'='*55}")
    print(f"  {msg}")
    print(f"{'='*55}")

def step(msg):
    print(f"  [OK] {msg}")

def error(msg):
    print(f"  [FAILED] {msg}")
    sys.exit(1)

# ── Step 1: Connect to MySQL ───────────────────────────────────────────────────
banner("STEP 1: Connecting to MySQL Server...")
try:
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset=CHARSET
    )
    cursor = conn.cursor()
    step(f"Connected to MySQL at {MYSQL_HOST}:{MYSQL_PORT}")
except pymysql.err.OperationalError as e:
    error(f"Cannot connect to MySQL!\n\n"
          f"  - Make sure XAMPP MySQL is RUNNING\n"
          f"  - Check: XAMPP Control Panel > MySQL > Start\n\n"
          f"  Technical: {e}")

# ── Step 2: Create Database ───────────────────────────────────────────────────
banner("STEP 2: Creating Database...")
try:
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        f"CHARACTER SET {CHARSET} COLLATE {CHARSET}_unicode_ci"
    )
    conn.commit()
    step(f"Database '{DB_NAME}' created successfully!")
except Exception as e:
    error(f"Failed to create database: {e}")

# ── Step 3: Close raw connection & use Flask-SQLAlchemy ──────────────────────
cursor.close()
conn.close()

banner("STEP 3: Creating all tables via Flask-SQLAlchemy...")
try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.create_all()
        step("All tables created successfully!")

    # Count tables
    conn2 = pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=DB_NAME, charset=CHARSET
    )
    c2 = conn2.cursor()
    c2.execute("SHOW TABLES")
    tables = c2.fetchall()
    conn2.close()

    step(f"Total tables in database: {len(tables)}")
    for t in tables:
        print(f"       - {t[0]}")

except Exception as e:
    error(f"Flask table creation failed: {e}")

# ── Done! ─────────────────────────────────────────────────────────────────────
banner("✅ SETUP COMPLETE!")
print("""
  Your system is now configured to use MySQL.

  Next steps:
  1. Make sure XAMPP MySQL is always running before starting the app
  2. Run:  python run.py
  3. Login and start using the system!

  Database:  rays_pos_db
  Host:      localhost:3306
  User:      root (no password)
""")
