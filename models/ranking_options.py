from tracemalloc import start
from db.database import get_db_connection
import time

def ranking_options(source=None, subject=None):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all ranking tables
    cursor.execute('''
                   SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_Rankings'
                   ORDER BY RANDOM()
                   ''')
    tables = [row[0] for row in cursor.fetchall()]
    results = []

    for table in tables:
        # Get all source/subject combinations and their top 3 universities in one query
        query = f'''
            SELECT source, subject, normalized_name, rank_value, name
            FROM (
                SELECT source, subject, "{table}".normalized_name, rank_value, universities.name,
                       ROW_NUMBER() OVER (PARTITION BY source, subject ORDER BY rank_value ASC) as rn
                FROM "{table}"
                LEFT JOIN universities ON universities.normalized_name = "{table}".normalized_name
            ) t
            WHERE rn <= 3
        '''
        cursor.execute(query)
        rows = cursor.fetchall()

        # Group results by source/subject
        grouped = {}
        for src, subj, normalized_name, rank_value, name in rows:
            # Apply filters
            if (source and src != source) or (subject and subject not in subj):
                continue

            key = (src, subj)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append({
                'normalized_name': normalized_name,
                'rank_value': rank_value,
                'name': name
            })

        # Add to results
        for (src, subj), top_unis in grouped.items():
            results.append({
                'table': table,
                'source': src,
                'subject': subj,
                'top_universities': top_unis
            })

    conn.close()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Duration: {duration} seconds")
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