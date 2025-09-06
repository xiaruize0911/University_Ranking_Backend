from tracemalloc import start
from db.database import get_db_connection
import time

def ranking_options(source=None, subject=None):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query 1: Get all ranking tables
    table_query = '''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE '%_Rankings'
        ORDER BY name
    '''
    cursor.execute(table_query)
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        conn.close()
        return []

    # Query 2: Create a temporary table and populate it with all results
    # This avoids the UNION limit by using INSERT statements instead
    cursor.execute('''
        CREATE TEMPORARY TABLE temp_rankings (
            table_name TEXT,
            source TEXT,
            subject TEXT,
            normalized_name TEXT,
            rank_value INTEGER
        )
    ''')

    # Insert data from each table into temp table (still one query execution)
    insert_queries = []
    subject_underscore = subject.replace(" ", "_") if subject else None
    for table in tables:
        # Build the SELECT for this table with all filters
        select_part = f'''
            SELECT '{table}', source, subject, normalized_name, rank_value
            FROM "{table}"
            WHERE rank_value <= 3
        '''
        # Add source filter
        if source:
            select_part += f" AND source = '{source}'"
        # Add subject filter  
        if subject:
            select_part += f" AND (subject LIKE '%{subject}%' OR subject LIKE '%{subject_underscore}%')"

        insert_queries.append(f"INSERT INTO temp_rankings {select_part}")

    # Execute all inserts as a single transaction
    cursor.execute("BEGIN TRANSACTION")
    for insert_query in insert_queries:
        cursor.execute(insert_query)
    cursor.execute("COMMIT")

    # Now get the final results with universities join and top 3 filtering
    final_query = '''
        WITH ranked_data AS (
            SELECT table_name, source, subject, normalized_name, rank_value,
                   ROW_NUMBER() OVER (PARTITION BY table_name, source, subject ORDER BY rank_value) as rn
            FROM temp_rankings
        )
        SELECT r.table_name, r.source, r.subject, r.normalized_name, r.rank_value, u.name, T.chinese_name
        FROM ranked_data r
        LEFT JOIN universities u ON u.normalized_name = r.normalized_name
        LEFT JOIN University_names_en_to_zh AS T ON u.id = T.id
        WHERE r.rn <= 3
        ORDER BY r.table_name, r.source, r.subject, r.rank_value
    '''

    cursor.execute(final_query)
    results = cursor.fetchall()

    # Clean up temp table
    cursor.execute("DROP TABLE temp_rankings")

    # Group results efficiently
    grouped = {}
    for table_name, src, subj, normalized_name, rank_value, name, chinese_name in results:
        key = (table_name, src, subj)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append({
            'normalized_name': normalized_name,
            'rank_value': rank_value,
            'name': name,
            'chinese_name': chinese_name
        })

    # Convert to final format
    all_results = []
    for (table_name, src, subj), top_unis in grouped.items():
        all_results.append({
            'table': table_name,
            'source': src,
            'subject': subj,
            'top_universities': top_unis
        })

    conn.close()
    end_time = time.time()
    duration = end_time - start_time
    print(f"Duration: {duration} seconds found {len(all_results)} results")
    return all_results

def get_ranking_detail(table_name, source, subject):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all universities in the specified table
    cursor.execute(f'''
                   SELECT "{table_name}".normalized_name, rank_value, universities.name, T.chinese_name FROM "{table_name}"
                   LEFT JOIN universities ON universities.normalized_name = "{table_name}".normalized_name
                   LEFT JOIN University_names_en_to_zh AS T ON universities.id = T.id
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
        chinese_name = row[3]
        processed_results.append({'normalized_name': normalized_name, 'rank_value': rank_value, 'name': name, 'chinese_name': chinese_name})
    
    conn.close()
    return processed_results