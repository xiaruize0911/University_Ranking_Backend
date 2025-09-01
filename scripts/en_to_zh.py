import sqlite3
import requests
import json
import os
import time
import uuid

# Bing Translator API details (replace with your actual API key and endpoint)
# API_KEY = os.getenv('BING_TRANSLATOR_API_KEY')  # Load from environment variable
# LOCATION = os.getenv('BING_TRANSLATOR_LOCATION')  # Load region/location from environment variable (e.g., 'eastus')
API_KEY = '5MnbgXXvHjpKY7sXvPy72QS5HdERHwYUapEgKuz915bqS4zHIRrHJQQJ99BHAC3pKaRXJ3w3AAAbACOGvX8l'
LOCATION = 'eastasia'
if not API_KEY:
    raise ValueError("BING_TRANSLATOR_API_KEY environment variable is not set. Please set it to your valid Bing Translator API key.")
if not LOCATION:
    raise ValueError("BING_TRANSLATOR_LOCATION environment variable is not set. Please set it to your resource location (e.g., 'eastus').")

ENDPOINT = 'https://api.cognitive.microsofttranslator.com'  # Base endpoint
PATH = '/translate'
CONSTRUCTED_URL = ENDPOINT + PATH

# Headers for the API request
HEADERS = {
    'Ocp-Apim-Subscription-Key': API_KEY,
    'Ocp-Apim-Subscription-Region': LOCATION,  # Required for regional resources
    'Content-Type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())  # For tracing
}

def translate_batch(texts, retries=3):
    """Translate a list of texts from English to Chinese using Bing Translator API with retry logic."""
    body = [{'text': text} for text in texts]
    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': 'zh'
    }
    for attempt in range(retries):
        response = requests.post(CONSTRUCTED_URL, params=params, headers=HEADERS, json=body)
        if response.status_code == 200:
            result = response.json()
            return [item['translations'][0]['text'] for item in result]
        elif response.status_code == 401:
            print(f"Authorization failed (401) for batch: Check your API key and region. Response: {response.text}")
            return None  # No retry for auth errors
        else:
            print(f"Translation failed for batch (attempt {attempt+1}/{retries}): {response.status_code} - {response.text}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    return None

def main():
    # Connect to the database
    conn = sqlite3.connect('../University_rankings_copy.db')
    cursor = conn.cursor()

    # Query to get university names from Universities table
    cursor.execute("SELECT id, name FROM Universities")
    universities = cursor.fetchall()

    # Create the new table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS University_names_en_to_zh (
            id INTEGER PRIMARY KEY,
            english_name TEXT,
            chinese_name TEXT
        )
    ''')

    # Process in batches of 100
    batch_size = 1000
    for i in range(0, len(universities), batch_size):
        batch = universities[i:i + batch_size]
        batch_ids = [univ_id for univ_id, _ in batch]
        batch_names = [name for _, name in batch if name]  # Filter out None names
        
        if batch_names:
            translated_batch = translate_batch(batch_names)
            if translated_batch:
                for (univ_id, name), translated in zip(batch, translated_batch):
                    cursor.execute('''
                        INSERT INTO University_names_en_to_zh (id, english_name, chinese_name)
                        VALUES (?, ?, ?)
                    ''', (univ_id, name, translated))
                    print(f"Translated and inserted: {name} -> {translated}")
            else:
                print(f"Skipped batch starting at index {i} (translation failed)")
        time.sleep(60)

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Translation process completed.")

if __name__ == "__main__":
    main()