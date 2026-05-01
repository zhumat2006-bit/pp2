import psycopg2
from config import load_config
import os


def get_connection():
    try:
        return psycopg2.connect(**load_config())
    except Exception as error:
        print(f"Connection error: {error}")
        return None


def setup_database():
    conn = get_connection()

    if not conn:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                if os.path.exists("schema.sql"):
                    with open("schema.sql", "r", encoding="utf-8") as file:
                        cur.execute(file.read())

                if os.path.exists("procedures.sql"):
                    with open("procedures.sql", "r", encoding="utf-8") as file:
                        cur.execute(file.read())

        print("Database schema and procedures initialized successfully!")

    except Exception as error:
        print(f"Database setup error: {error}")

    finally:
        conn.close()


if __name__ == "__main__":
    setup_database()