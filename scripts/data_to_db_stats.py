import json
import sqlite3
import re
import pandas as pd
import numbers
from Backend.utils.utils import normalize_name

# Load JSON data
university = pd.read_json("data/usnews_detailed_data.json")
# Normalize university name for DB matching

university["normalized_name"] = university['Name']
university['normalized_name'] = university['normalized_name'].apply(normalize_name)

# Detect all fields that contain 'number' (case-insensitive)
stats_data = []
for keys, school in university.iterrows():
    # print(school)
    nameCur = school['normalized_name']
    for key, value in school.items():
        # print(key,key.lower())
        if "number" in key.lower():
            if isinstance(value, numbers.Number):
                continue
            try:
                count = int(value.replace(",", ""))
                stat_type = key # snake_case
                stats_data.append((nameCur, stat_type, count))
            except (ValueError, TypeError):
                continue
                # print(f"⚠️ Skipped non-numeric value: {value} for key '{key}'")

print(stats_data)

# Insert into SQLite
conn = sqlite3.connect("University_rankings.db")
cursor = conn.cursor()

cursor.executemany("""
    INSERT INTO UniversityStats (normalized_name, type, count)
    VALUES (?, ?, ?)
""", stats_data)

conn.commit()
conn.close()

print(f"✅ Inserted {len(stats_data)} dynamic 'number' stats for: {university['Name']}")
