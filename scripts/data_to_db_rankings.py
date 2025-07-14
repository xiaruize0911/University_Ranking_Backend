import pandas as pd
import numbers
import sqlite3

import pandas as pd
import csv
import re
import json

ALIASES = {
    'mit': 'massachusetts institute of technology',
    'caltech': 'california institute of technology',
    'ucb': 'university of california berkeley',
    'stanford': 'stanford university',
    # Add more aliases as needed
}

def normalize_name(name: str) -> str:
    # Lowercase
    name = name.lower()
    # Remove text in parentheses, like "(MIT)"
    name = re.sub(r'\(.*?\)', '', name)
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    # Normalize spaces
    name = re.sub(r'\s+', ' ', name)
    if name in ALIASES:
        # If the name is an alias, replace it with the full name
        name = ALIASES[name]
    return name.strip()

# Load the CSV
df = pd.read_json("../data/usnews_detailed_data.json")

# Make sure normalized name exists
# if "normalizedName" not in df.columns:
#     raise ValueError("Missing 'normalizedName' column in CSV")

# Connect to SQLite database
conn = sqlite3.connect("../University_rankings.db")
cursor = conn.cursor()

# Columns to ignore (non-ranking data)
non_ranking_columns = {
    "Name", "normalizedName", "Country", "Country Code", "City", "Photo", "Blurb"
}

# Automatically find ranking columns
ranking_columns = [
    col for col in df.columns if col not in non_ranking_columns and df[col].dtype in [float, int]
]

# print(f"🔍 Detected ranking columns: {ranking_columns}")

rows_inserted = 0

# Loop over each row in the DataFrame
for _, row in df.iterrows():
    normalized_name = normalize_name(row.get('Name'))
    for col in ranking_columns:
        rank_value = row[col]
        if pd.notna(rank_value):
            # Attempt to extract source and subject from column name
            parts = col.split("_", 1)
            if len(parts) == 2:
                source, subject = parts
            else:
                source, subject = "US_News", col
            if "SCORE" in subject or "Index" in subject:
                continue
            if not isinstance(rank_value, numbers.Number):
                continue
            # print(normalized_name,source,subject,rank_value,sep=',')
            # Insert into the Rankings table
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

# Finalize
conn.commit()
conn.close()

print(f"✅ Inserted {rows_inserted} ranking rows into Rankings table.")
