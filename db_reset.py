import psycopg2

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "192837",
    "host": "127.0.0.1",
    "port": "5432"
}

def clear_database():
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        print("Connected")

        cur.execute("TRUNCATE TABLE device_logs RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE scenarios RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE devices RESTART IDENTITY CASCADE;")

        conn.commit()
        print("Everything is working")

        cur.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    clear_database()