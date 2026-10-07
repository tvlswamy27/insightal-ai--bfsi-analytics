import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get("DB_HOST", "127.0.0.1")
port = int(os.environ.get("DB_PORT", 3306))
user = os.environ.get("DB_USER", "root")
password = os.environ.get("DB_PASSWORD", "")

print(f"Connecting to MySQL at {host}:{port} as {user}...")

try:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"MySQL Version: {version[0]}")
        
        cursor.execute("SELECT DATABASE();")
        db = cursor.fetchone()
        print(f"Current Database: {db[0]}")
        
    connection.close()
    print("Connection test successful!")

except Exception as e:
    print(f"Connection failed: {e}")
