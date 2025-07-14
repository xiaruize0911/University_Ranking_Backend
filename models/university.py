from db.database import get_db_connection

def get_university_by_id(univ_id):
    conn = get_db_connection()
    
    # Step 1: Get university basic info
    cur = conn.execute("SELECT * FROM Universities WHERE id = ?", (univ_id,))
    row = cur.fetchone()
    if not row:
        return None

    university = dict(row)
    normalized_name = university['normalized_name']

    # Step 2: Get rankings from all *_Rankings tables
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_Rankings'")
    ranking_tables = [r["name"] for r in cur.fetchall()]
    rankings = []
    for table in ranking_tables:
        try:
            cur = conn.execute(
                f"""SELECT subject, source, rank_value 
                    FROM "{table}" WHERE normalized_name = ?""",
                (normalized_name,)
            )
            rankings += [dict(r) for r in cur.fetchall()]
        except Exception as e:
            # Skip malformed or mismatched tables
            continue
    # Step 3: Get stats from UniversityStats
    cur = conn.execute(
        "SELECT type, count, year FROM UniversityStats WHERE normalized_name = ?",
        (normalized_name,)
    )
    stats = [dict(r) for r in cur.fetchall()]
    
    conn.close()

    # Combine everything
    university["rankings"] = rankings
    university["stats"] = stats
    return university

def get_universities_by_name(name):
    conn = get_db_connection()
    cur = conn.execute("SELECT * FROM Universities WHERE name LIKE ?", (f"%{name}%",))
    if cur.rowcount == 0:
        return []
    res = get_university_by_id(cur.fetchone()["id"])
    conn.close()
    return res