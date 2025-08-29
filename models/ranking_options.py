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

    if not tables:
        conn.close()
        return []

    # Process tables in batches and create temporary views
    batch_size = 15  # Smaller batch size for view creation
    view_names = []

    for i in range(0, len(tables), batch_size):
        batch_tables = tables[i:i + batch_size]
        view_name = f"batch_view_{i//batch_size}"

        # Create UNION query for this batch
        union_parts = []
        for table in batch_tables:
            union_parts.append(f'''
                SELECT '{table}' as table_name, source, subject, normalized_name, rank_value
                FROM "{table}"
            ''')

        union_query = ' UNION ALL '.join(union_parts)

        # Create temporary view for this batch
        cursor.execute(f'''
            CREATE TEMPORARY VIEW {view_name} AS
            {union_query}
        ''')
        view_names.append(view_name)

    # Now union all the batch views
    if len(view_names) == 1:
        # Only one batch, use it directly
        final_view_query = f"SELECT * FROM {view_names[0]}"
    else:
        # Union all batch views
        view_union_parts = [f"SELECT * FROM {view}" for view in view_names]
        final_view_query = ' UNION ALL '.join(view_union_parts)

    # Create final combined view
    cursor.execute(f'''
        CREATE TEMPORARY VIEW all_rankings AS
        {final_view_query}
    ''')

    # Single query using the final view
    query = '''
        SELECT ar.table_name, ar.source, ar.subject, ar.normalized_name, ar.rank_value, u.name
        FROM (
            SELECT table_name, source, subject, normalized_name, rank_value,
                   ROW_NUMBER() OVER (PARTITION BY source, subject ORDER BY rank_value ASC) as rn
            FROM all_rankings
        ) ar
        LEFT JOIN universities u ON u.normalized_name = ar.normalized_name
        WHERE ar.rn <= 3
    '''

    # Apply filters
    params = []
    if source:
        query += " AND ar.source = ?"
        params.append(source)
    if subject:
        query += " AND ar.subject LIKE ?"
        params.append(f"%{subject}%")

    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Group results
    grouped = {}
    for table_name, src, subj, normalized_name, rank_value, name in rows:
        key = (table_name, src, subj)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append({
            'normalized_name': normalized_name,
            'rank_value': rank_value,
            'name': name
        })

    # Convert to final format
    results = []
    for (table_name, src, subj), top_unis in grouped.items():
        results.append({
            'table': table_name,
            'source': src,
            'subject': subj,
            'top_universities': top_unis
        })

    # Clean up all temporary views
    for view_name in view_names:
        cursor.execute(f'DROP VIEW IF EXISTS {view_name}')
    cursor.execute('DROP VIEW IF EXISTS all_rankings')

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