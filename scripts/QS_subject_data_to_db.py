import os
import pandas as pd
import sqlite3
import re

def normalize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

# Path to the QS subject CSVs
subject_dir = '/Users/xiaruize/Documents/Code/Software Engineering/University_Ranking/Scraper/QS_WUR_by_Subject'
subject_files = [f for f in os.listdir(subject_dir) if f.endswith('.csv')]


rows_inserted = 0

for file in subject_files:
    conn = sqlite3.connect('/Users/xiaruize/Documents/Code/Software Engineering/University_Ranking/University_Ranking_Backend/University_rankings.db')
    cursor = conn.cursor()
    file_path = os.path.join(subject_dir, file)
    # Skip files that are not subject data
    try:
        df = pd.read_csv(file_path, skiprows=10)
    except Exception as e:
        print(f"❌ Failed to read {file}: {e}")
        continue
    if df.empty or 'Institution' not in df.columns:
        print(f"⚠️ Skipping {file} (no data)")
        continue
    subject = file.replace('.csv', '')
    source = 'QS'

    for _, row in df.iterrows():
        name = row['Institution']
        normalized_name = normalize_name(name)
        rank_raw = row['2025']
        rank_value = None
        if pd.notna(rank_raw):
            if isinstance(rank_raw, str) and rank_raw.startswith('='):
                # Handle equal rank, e.g., '=12' -> 12
                try:
                    rank_value = int(rank_raw.lstrip('=').split('-')[0].strip())
                except Exception:
                    rank_value = None
            elif isinstance(rank_raw, str) and '-' in rank_raw:
                # Handle range, e.g., '201-250' -> 201
                try:
                    rank_value = int(rank_raw.split('-')[0].strip())
                except Exception:
                    rank_value = None
            else:
                try:
                    rank_value = int(rank_raw)
                except Exception:
                    rank_value = None
        if rank_value is None:
            print(f"⚠️ Skipping {name} (invalid rank: {rank_raw})")
        if not normalized_name or rank_value is None:
            continue
        table_name = f'{source}_{subject}_Rankings'
        sql_query = f'''
            CREATE TABLE IF NOT EXISTS "{table_name}"(
                normalized_name TEXT,
                source TEXT,
                subject TEXT,
                rank_value INTEGER
            )
        '''
        cursor.execute(sql_query)
        try:
            cursor.execute(f'''
                INSERT INTO "{table_name}" (normalized_name, source, subject, rank_value)
                VALUES (?, ?, ?, ?)
            ''', (normalized_name, source, subject, rank_value))
            rows_inserted += 1
        except Exception as e:
            print(f"❌ Insert failed for {normalized_name} in {subject}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Inserted {rows_inserted} QS subject ranking rows into the database.")
