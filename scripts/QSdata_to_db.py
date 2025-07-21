import csv
import json
import codecs
import re
import pandas as pd
import sqlite3

conn = sqlite3.connect('../University_rankings.db')

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

with open('../data/2026_QS_World_University_Rankings_1.0.csv', mode='r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    data=list(reader)

data = json.loads(json.dumps(data))

for row in data:
    if 'Country/Territory' in row:
        row['Country'] = row.pop('Country/Territory')
    if 'Rank' in row:
        if '-' in row['Rank']:
            row['Rank'] = row['Rank'].split('-')[0]
        elif '+' in row['Rank']:
            row['Rank'] = row['Rank'].split('+')[0]
        row['Rank']=int(row['Rank'])
    row['normalized_name'] = normalize_name(row['Name'])
json_data = json.dumps(data,indent=4)

conn.execute('''
    CREATE TABLE QS_World_University_Rankings (
                normalized_name TEXT,
                source TEXT,
                subject TEXT,
                rank_value INTEGER
            )
''')

data_counter = 0

for row in data:
    try:
        conn.execute('''
            INSERT INTO QS_World_University_Rankings (normalized_name, source, subject, rank_value)
            VALUES (?,?,?,?)
        ''', (row['normalized_name'],'QS', 'World University Rankings', row['Rank']))
        data_counter += 1
    except sqlite3.IntegrityError:
        print(f"Duplicate entry for {row['normalized_name']}")

print(f"Inserted {data_counter} rows into the database.")

conn.commit()
conn.close()