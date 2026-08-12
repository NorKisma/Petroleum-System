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
        cursor.execute("SELECT module_hrm FROM tenants LIMIT 1")
        print("Success!")
        row = cursor.fetchone()
        print(row)
finally:
    conn.close()
