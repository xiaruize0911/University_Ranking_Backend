"""Create index on University_names_en_to_zh(normalized_name) if it doesn't exist.

Usage: python3 scripts/add_index_normalized.py
"""
import sqlite3
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, 'University_rankings.db')

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check if index exists
cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='University_names_en_to_zh' AND name='idx_univ_names_normalized';")
if cur.fetchone():
    print('Index idx_univ_names_normalized already exists')
else:
    print('Creating index idx_univ_names_normalized on University_names_en_to_zh(normalized_name)')
    cur.execute('CREATE INDEX idx_univ_names_normalized ON University_names_en_to_zh(normalized_name);')
    conn.commit()
    print('Index created')

conn.close()
