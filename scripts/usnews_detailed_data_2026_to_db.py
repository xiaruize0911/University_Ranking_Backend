import pandas as pd
import sqlite3
import numbers
import re
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.normalize_name import normalize_name

# Load the new US News data
with open("data/usnews_detailed_data_2026.json", "r") as f:
    data = json.load(f)

# Convert to DataFrame for easier handling
university = pd.DataFrame(data)

# Normalize university name for DB matching
university["normalized_name"] = university['Name'].apply(normalize_name)

# Insert/Update Universities table
conn = sqlite3.connect("../University_rankings.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Universities (
    id INTEGER PRIMARY KEY,
    normalized_name TEXT UNIQUE,
    name TEXT,
    country TEXT,
    country_code TEXT,
    city TEXT,
    photo TEXT,
    blurb TEXT
)
""")

cntid = 0
for _, row in university.iterrows():
    cntid+=1
    cursor.execute("""
        INSERT OR IGNORE INTO Universities (id, normalized_name, name, country, country_code, city, photo, blurb)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cntid, row["normalized_name"], row["Name"], row.get("Country", None), row.get("Country Code", None), row.get("City", None), row.get("Image", None), row.get("Description", None)
    ))

# Insert stats
stats_data = []
for _, school in university.iterrows():
    nameCur = school['normalized_name']
    for key, value in school.items():
        if isinstance(key, str) and "number" in key.lower():
            if isinstance(value, numbers.Number):
                count = value
            else:
                try:
                    count = int(str(value).replace(",", ""))
                except (ValueError, TypeError):
                    continue
            stat_type = key
            stats_data.append((nameCur, stat_type, count))

cursor.executemany("""
    INSERT INTO UniversityStats (normalized_name, type, count)
    VALUES (?, ?, ?)
""", stats_data)

# Insert rankings
non_ranking_columns = {
    "Name", "normalized_name", "Country", "Country Code", "City", "Image", "Description"
}
ranking_columns = [col for col in university.columns if col not in non_ranking_columns and university[col].dtype in [float, int]]
rows_inserted = 0
for _, row in university.iterrows():
    normalized_name = row['normalized_name']
    for col in ranking_columns:
        rank_value = row[col]
        if pd.notna(rank_value):
            parts = col.split("_", 1)
            if len(parts) == 2:
                source, subject = parts
            else:
                source, subject = "US_News", col
            if "SCORE" in subject or "Index" in subject:
                continue
            if not isinstance(rank_value, numbers.Number):
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
                cursor.execute(f"""
                    INSERT INTO "{table_name}" (normalized_name, source, subject, rank_value)
                    VALUES (?, ?, ?, ?)
                """, (normalized_name, source, subject, rank_value))
                rows_inserted += 1
            except Exception as e:
                print(f"❌ Insert failed for {normalized_name} - {col}: {e}")

conn.commit()
conn.close()
print(f"✅ Imported US News 2026 data: {len(university)} universities, {len(stats_data)} stats, {rows_inserted} rankings.")
