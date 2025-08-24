import json
import sqlite3
import re
from urllib.parse import urlparse

def normalize_name(name: str) -> str:
    """Normalize university name for consistent matching."""
    name = name.lower()
    name = re.sub(r'\(.*?\)', '', name)  # Remove parentheses and content
    name = re.sub(r'[^\w\s]', '', name)  # Remove special characters
    name = re.sub(r'\s+', ' ', name)     # Normalize whitespace
    return name.strip()

def extract_subject_from_url(url: str) -> str:
    """Extract subject name from Niche URL."""
    # Extract the path from URL
    path = urlparse(url).path
    
    # Extract subject from patterns like:
    # /colleges/search/best-colleges-for-art/ -> art
    # /colleges/search/best-colleges-with-ceramics/ -> ceramics
    
    if 'best-colleges-for-' in path:
        subject = path.split('best-colleges-for-')[1].rstrip('/')
    elif 'best-colleges-with-' in path:
        subject = path.split('best-colleges-with-')[1].rstrip('/')
    else:
        # Fallback: use the entire path segment
        segments = [seg for seg in path.split('/') if seg]
        subject = segments[-1] if segments else 'unknown'
    
    # Clean up the subject name
    subject = subject.replace('-', '_')
    return subject

def main():
    """Main function to process Niche rankings and insert into database."""
    
    # File paths
    json_file = '/Users/xiaruize/Documents/Code/Software Engineering/University_Ranking/University_Ranking_Backend/data/niche_college_rankings_fixed.json'
    db_file = '/Users/xiaruize/Documents/Code/Software Engineering/University_Ranking/University_Ranking_Backend/University_rankings.db'
    
    print(f"📖 Reading Niche rankings from: {json_file}")
    
    # Read the fixed JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read JSON file: {e}")
        return
    
    print(f"✅ Loaded {len(data)} Niche ranking categories")
    
    rows_inserted = 0
    
    for url, universities in data.items():
        # Connect to database for each category (following QS script pattern)
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Extract subject from URL
        subject = extract_subject_from_url(url)
        source = 'Niche'
        
        print(f"🔄 Processing {subject} with {len(universities)} universities...")
        
        # Create table name
        table_name = f'{source}_{subject}_Rankings'
        
        # Create table if it doesn't exist - using exact same structure as QS script
        sql_query = f'''
            CREATE TABLE IF NOT EXISTS "{table_name}"(
                normalized_name TEXT,
                source TEXT,
                subject TEXT,
                rank_value INTEGER
            )
        '''
        cursor.execute(sql_query)
        
        # Insert university rankings
        for rank, university_name in enumerate(universities, 1):
            normalized_name = normalize_name(university_name)
            
            # Skip if normalized name is empty or rank is invalid (following QS pattern)
            if not normalized_name:
                print(f"⚠️ Skipping {university_name} (invalid name)")
                continue
                
            try:
                cursor.execute(f'''
                    INSERT INTO "{table_name}" (normalized_name, source, subject, rank_value)
                    VALUES (?, ?, ?, ?)
                ''', (normalized_name, source, subject, rank))
                rows_inserted += 1
            except Exception as e:
                print(f"❌ Insert failed for {normalized_name} in {subject}: {e}")
        
        conn.commit()
        conn.close()
    
    print(f"✅ Inserted {rows_inserted} Niche ranking rows into the database.")

if __name__ == "__main__":
    main()
