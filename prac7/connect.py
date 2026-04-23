import psycopg2
from config import DB_CONFIG

def create_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def create_table():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            phone VARCHAR(20) UNIQUE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()