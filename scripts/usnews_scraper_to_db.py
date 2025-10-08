import requests
import sqlite3
import re
import time
import argparse

from tqdm import tqdm

# Function to normalize university names
def normalize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r'\(.*?\)', '', name)  # Remove text in parentheses
    name = re.sub(r'[\W_]+', ' ', name)  # Remove non-alphanumeric characters
    return name.strip()

# Base URL for the API
BASE_URL = "https://www.usnews.com/best-colleges/api/search?_page="

# Define headers to mimic a browser
HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:138.0) Gecko/20100101 Firefox/138.0'
}

# Fetch data from all pages
rankings = []
total_pages = 183  # From the API response

for page in tqdm(range(1, total_pages + 1)):
    url = f"{BASE_URL}{page}"
    try:
        print(f'Fetching {url}')
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("data", {}).get("items", [])
        for item in items:
            institution = item.get("institution", {})
            if institution.get('schoolType') != 'national-universities':
                continue
            rank = institution.get("rankingSortRank")
            name = institution.get("displayName")
            if rank and name:
                rankings.append((rank, normalize_name(name)))
        
        print(f"✅ Fetched page {page}/{total_pages}")
        # time.sleep(1)  # Be respectful to the server
        
    except Exception as e:
        print(f"❌ Failed to fetch page {page}: {e}")
        continue

with open('usnews_national_rankings.txt', 'w') as f:
    f.write('\n'.join([f"{rank},{name}" for rank, name in rankings]))

# rankings = []
# with open('usnews_national_rankings.txt', 'r') as f:
#     for line in f:
#         rank, name = line.strip().split(',')
#         rankings.append((int(rank), name))

# Connect to the SQLite database (copy)
conn = sqlite3.connect("../University_rankings.db")
cursor = conn.cursor()

# Define source and subject
source = 'US_News'
subject = 'Best global universities in united states'
table_name = 'US_News_best global universities in united states_Rankings'

# Create table if not exists (following Niche script pattern)
sql_query = f'''
    CREATE TABLE IF NOT EXISTS "{table_name}"(
        normalized_name TEXT,
        source TEXT,
        subject TEXT,
        rank_value INTEGER
    )
'''
cursor.execute(sql_query)


def confirm(prompt: str) -> bool:
    try:
        return input(prompt).strip().lower() in ("y", "yes")
    except Exception:
        return False


def main(force: bool = False):
    # Before inserting, delete existing rows for this source/subject to replace with fresh data
    if not force:
        print(f"About to DELETE existing rows in table '{table_name}' for source='{source}', subject='{subject}'")
        if not confirm("Proceed? [y/N]: "):
            print("Aborting — no changes made to the database.")
            conn.close()
            return

    try:
        cursor.execute(f"DELETE FROM \"{table_name}\" WHERE source = ? AND subject = ?", (source, subject))
        print("Deleted existing rows for this source/subject (if any).")
    except Exception as e:
        print(f"Failed to delete existing rows: {e}")
        conn.close()
        return

    rows_inserted = 0
    for rank, normalized_name in rankings:
        try:
            cursor.execute(f"""
                INSERT INTO "{table_name}" (normalized_name, source, subject, rank_value)
                VALUES (?, ?, ?, ?)
            """, (normalized_name, source, subject, rank))
            rows_inserted += 1
        except sqlite3.IntegrityError as e:
            print(f"Skipping duplicate entry for {normalized_name}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Inserted {rows_inserted} rows into the database.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape US News national rankings and store into SQLite DB (replace existing rows).')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt and replace existing rows')
    args = parser.parse_args()
    main(force=args.force)
