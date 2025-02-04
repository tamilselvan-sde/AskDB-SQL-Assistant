import sqlite3

def fetch_all_data():
    """Fetch all tables and their data dynamically from the database."""
    conn = sqlite3.connect("Ecommerce.db")
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Dictionary to hold all tables and their corresponding data
    all_tables_data = {}

    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT * FROM {table_name}")  # Fetch data from each table
        rows = cursor.fetchall()

        # Fetch column names for each table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]

        # Store table name and corresponding data
        all_tables_data[table_name] = {
            "columns": columns,
            "data": rows
        }

    conn.close()
    return all_tables_data
