from db.database import get_db_connection

def get_cities_db(country=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if country:
        cursor.execute("""
            SELECT DISTINCT city FROM Universities
            WHERE country = ?
            ORDER BY city ASC NULLS LAST
        """, (country,))
    else:
        cursor.execute("""
            SELECT DISTINCT city FROM Universities
            ORDER BY city ASC NULLS LAST
        """)

    cities = [row["city"] for row in cursor.fetchall()]
    conn.close()
    cities.pop()
    return cities