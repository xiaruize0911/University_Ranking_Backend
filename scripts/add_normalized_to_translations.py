"""Script to ensure `normalized_name` column exists in University_names_en_to_zh and populate it.

Usage: python3 scripts/add_normalized_to_translations.py

This will:
 - connect to the local SQLite database `University_rankings.db` in the repo root
 - add a `normalized_name` TEXT column to `University_names_en_to_zh` if it doesn't exist
 - populate `normalized_name` by normalizing `english_name` using `utils.normalize_name.normalize_name`
 - print a short summary of how many rows were updated
"""
import sqlite3
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, 'University_rankings.db')

# Ensure utils can be imported
sys.path.insert(0, REPO_ROOT)
from utils.normalize_name import normalize_name


def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Check columns
    cur.execute("PRAGMA table_info('University_names_en_to_zh');")
    cols = [r[1] for r in cur.fetchall()]

    if 'normalized_name' not in cols:
        print('Adding column normalized_name to University_names_en_to_zh')
        cur.execute('ALTER TABLE University_names_en_to_zh ADD COLUMN normalized_name TEXT')
        conn.commit()
    else:
        print('Column normalized_name already exists')

    # Count rows missing normalized_name or empty
    cur.execute("SELECT id, english_name, normalized_name FROM University_names_en_to_zh")
    rows = cur.fetchall()

    to_update = []
    for r in rows:
        en = r[1] or ''
        existing = r[2] or ''
        new_norm = normalize_name(en)
        if existing.strip() == '' or existing != new_norm:
            to_update.append((new_norm, r[0]))

    print(f"Updating {len(to_update)} rows")
    if to_update:
        cur.executemany("UPDATE University_names_en_to_zh SET normalized_name = ? WHERE id = ?", to_update)
        conn.commit()

    # Print sample rows
    cur.execute("SELECT id, english_name, normalized_name FROM University_names_en_to_zh LIMIT 10")
    for r in cur.fetchall():
        print(f"{r[0]} | {r[1]} | {r[2]}")

    conn.close()


if __name__ == '__main__':
    main()
