from db.database import get_db_connection

def get_countries_db():
    conn = get_db_connection()
    cur = conn.cursor()
    res = cur.execute("SELECT DISTINCT country FROM Universities ORDER BY country NULLS LAST")
    results = [dict(row) for row in res.fetchall()]
    results.pop()
    cur.close()
    return results