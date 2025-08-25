from db.database import get_db_connection

def ranking_options(source = None, subject = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all ranking tables
    cursor.execute('''
                   SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_Rankings' LIMIT 100
                   ''')
    tables = [row[0] for row in cursor.fetchall()]
    results = []
    for table in tables:
        # Get available sources and subjects in this table
        print(table)
        cursor.execute(f'SELECT DISTINCT source, subject FROM "{table}"')
        for src, subj in cursor.fetchall():
            # Optionally filter by source/subject
            if (source and src != source) or (subject and  subject not in subj):
                continue
            print(src, subj)
            # Get top 3 universities for this source/subject
            cursor.execute(f'''
                           SELECT "{table}".normalized_name,rank_value, name
                           FROM "{table}"
                           LEFT JOIN universities ON universities.normalized_name = "{table}".normalized_name
                           WHERE source = ? AND subject = ?
                           ORDER BY rank_value ASC LIMIT 3
                       ''', (src, subj))
            top_unis = cursor.fetchall()
            results.append({
                'table': table,
                'source': src,
                'subject': subj,
                'top_universities': [
                    {'normalized_name': u[0], 'rank_value': u[1],'name': u[2]} for u in top_unis
                ]
            })
    conn.close()
    return results

def get_ranking_detail(table_name, source, subject):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all universities in the specified table
    cursor.execute(f'''
                   SELECT "{table_name}".normalized_name, rank_value, name FROM "{table_name}"
                   LEFT JOIN universities ON universities.normalized_name = "{table_name}".normalized_name
                   WHERE source = ? AND subject = ?
                   ORDER BY rank_value ASC
                   ''', (source, subject))
    results = cursor.fetchall()
    
    # Convert rows to list and handle missing names
    processed_results = []
    for row in results:
        normalized_name = row[0]
        rank_value = row[1]
        name = row[2] if row[2] else normalized_name  # Use normalized_name if name is None
        processed_results.append({'normalized_name': normalized_name, 'rank_value': rank_value, 'name': name})
    
    conn.close()
    return processed_results