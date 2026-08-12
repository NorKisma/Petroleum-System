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
        for row in cursor.fetchall():
            print(row)
finally:
    conn.close()
