from db.database import get_db_connection
def ranking_options():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_Rankings'")
    tables = [row['name'] for row in cursor.fetchall()]

    conn.close()
    return tables
