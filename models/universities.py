from db.database import get_db_connection 
def filter_universities(query=None, sort_credit="US_News_best global universities_Rankings", country=None, city=None):
    conn = get_db_connection()
    # If a country-specific US News table exists, prefer that for sorting.
    # Expected table pattern: "US_News_best global universities in {country}_Rankings"
    join_table = sort_credit
    if country:
        # normalize country to match table naming used elsewhere (lowercase, trimmed)
        candidate_country = country.lower().strip()
        candidate_table = f"US_News_best global universities in {candidate_country}_Rankings"
        try:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (candidate_table,))
            if cur.fetchone():
                join_table = candidate_table
        except Exception:
            # If the metadata query fails, fall back to provided sort_credit
            join_table = sort_credit

    sql = """
        SELECT Universities.id,Universities.normalized_name, Universities.name, Universities.country, Universities.city, Universities.photo,
               R.rank_value
        FROM Universities
    """

    # If a ranking table is given, JOIN it
    if join_table:
        sql += f"""
            LEFT JOIN "{join_table}" AS R
            ON Universities.normalized_name = R.normalized_name
        """
    else:
        sql += """
            LEFT JOIN (SELECT NULL AS normalized_name, NULL AS rank_value) AS R
            ON 1 = 0
        """

    sql += " WHERE 1=1"
    params = []

    if query:
        sql += " AND (LOWER(Universities.name) LIKE ? OR LOWER(Universities.normalized_name) LIKE ?)"
        like = f"%{query.lower()}%"
        params += [like, like]

    if country:
        sql += " AND LOWER(Universities.country) = ?"
        params.append(country.lower())

    if city:
        sql += " AND LOWER(Universities.city) = ?"
        params.append(city.lower())
    # Always sort by rank_value if joined
    sql += " ORDER BY R.rank_value ASC NULLS LAST"
    sql += " LIMIT 200"

    cursor = conn.execute(sql, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results