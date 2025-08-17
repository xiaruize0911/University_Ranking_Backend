CREATE TABLE Universities (
    id INTEGER PRIMARY KEY,
    normalized_name text,
    name text,
    country text,
    country_code text,
    city text,
    photo text,
    blurb text
);
CREATE TABLE Rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    normalized_name text,
    source TEXT,
    -- e.g. 'QS', 'USNews'
    subject TEXT,
    -- e.g. 'Overall', 'Computer Science'
    rank_value REAL,
    year INTEGER DEFAULT 2025,
    FOREIGN KEY (university_id) REFERENCES Universities(id)
);