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

    rankings = sorted(rankings, key= lambda x: -1 if "global" in x["subject"] or "World" in x["subject"] else x["rank_value"])

    # Combine everything
    university["rankings"] = rankings
    university["stats"] = stats
    return university

def get_universities_by_name(name):
    conn = get_db_connection()
    print(name)
    cur = conn.execute("SELECT * FROM Universities WHERE normalized_name = ?", (f"{name}",))
    if cur.rowcount == 0:
        print("No university found")
        return []
    res = get_university_by_id(cur.fetchone()["id"])
    conn.close()
    return res

def get_university_rankings_by_source(normalized_name, source):
    conn = get_db_connection()
    
    # Get university basic info
    cur = conn.execute("SELECT name, country, city, photo FROM Universities WHERE normalized_name = ?", (normalized_name,))
    university_row = cur.fetchone()
    if not university_row:
        conn.close()
        return {"error": "University not found"}
    
    university_info = dict(university_row)
    
    # Get rankings from all *_Rankings tables for the specific source
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_Rankings'")
    ranking_tables = [r["name"] for r in cur.fetchall()]
    rankings = []
    
    for table in ranking_tables:
        try:
            cur = conn.execute(
                f"""SELECT subject, source, rank_value 
                    FROM "{table}" WHERE normalized_name = ? AND source = ?""",
                (normalized_name, source)
            )
            rankings += [dict(r) for r in cur.fetchall()]
        except Exception as e:
            # Skip malformed or mismatched tables
            continue
    
    conn.close()
    
    # Sort rankings by rank value
    rankings = sorted(rankings, key=lambda x: x["rank_value"] if x["rank_value"] else float('inf'))
    
    return {
        "university": university_info,
        "source": source,
        "rankings": rankings
    }