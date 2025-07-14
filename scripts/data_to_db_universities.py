import pandas as pd
import sqlite3

# Load the new CSV
df = pd.read_csv("data/merged_data.csv")

# Select and rename required columns
df = df[[
    "Name", "normalizedName", "Country", "Country Code", "City", "Photo", "Blurb"
]].copy()

# Rename to match SQL table
df.columns = [
    "name", "normalized_name", "country", "country_code", "city", "photo", "blurb"
]

# # Fill missing values with None (for SQLite NULL)
# df = df.fillna(0)

# Connect to SQLite database
conn = sqlite3.connect("University_rankings.db")
cursor = conn.cursor()

# Insert rows
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Universities (
            normalized_name, name, country, country_code, city, photo, blurb
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        row["normalized_name"], row["name"], row["country"],
        row["country_code"], row["city"], row["photo"], row["blurb"]
    ))

# Commit and close
conn.commit()
conn.close()

print("✅ Data inserted successfully into Universities table.")
