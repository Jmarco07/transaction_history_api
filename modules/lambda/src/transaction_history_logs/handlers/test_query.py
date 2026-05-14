import psycopg2
import os
from repositories.secrets_repository import SecretRepository

def test_redshift_query():
    creds = SecretRepository.get_redshift_credentials(
        secret_name=os.getenv("REDSHIFT_SECRET_NAME")
    )

    conn = psycopg2.connect(
        dbname=os.getenv("REDSHIFT_DATABASE_NAME"),
        user=creds["username"],
        password=creds["password"],
        host=os.getenv("REDSHIFT_ENDPOINT"),
        port=5439,
    )

    cur = conn.cursor()

    try:
        cur.execute("SELECT current_database(), current_user;")
        db, user = cur.fetchone()
        print(f"Connected to database: {db} as user: {user}")

        cur.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;")
        schemas = cur.fetchall()
        print("\n📑 All schemas:")
        for schema_name, in schemas:
            print(f" - {schema_name}")

        cur.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name
            LIMIT 50;
        """)
        tables = cur.fetchall()
        print("\n All accessible tables (first 50):")
        if tables:
            for schema, table in tables:
                print(f" - {schema}.{table}")
        else:
            print("No tables visible with current user/permissions.")

        try:
            cur.execute("SELECT * FROM target.data_load_metrics LIMIT 5;")
            rows = cur.fetchall()
            print("\n📄 Sample rows from target.data_load_metrics:")
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No rows found in target.data_load_metrics.")
        except psycopg2.errors.UndefinedTable:
            print("Table target.data_load_metrics does not exist or is not accessible.")

    except Exception as e:
        print("Query failed:", str(e))

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    test_redshift_query()
