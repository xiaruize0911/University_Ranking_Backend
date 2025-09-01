# University Ranking Backend API

A Flask-based REST API for university rankings data, providing comprehensive information about universities, their rankings across various sources, and supporting multiple languages (English and Chinese).

## Features

- **University Data**: Access detailed information about universities worldwide
- **Multi-source Rankings**: Rankings from QS, US News, Niche, and other sources
- **Multilingual Support**: University names available in both English and Chinese
- **Flexible Filtering**: Search and filter universities by various criteria
- **Ranking Details**: Detailed ranking information by source and subject
- **Dropdown Data**: Country, city, and ranking options for UI components

## Quick Start

### Prerequisites

- Python 3.8+
- SQLite3

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd University_Ranking_Backend
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the database file `University_rankings.db` is in the project root directory.

4. Run the application:

   ```bash
   python app.py
   ```

The API will be available at `http://localhost:10000`

## API Endpoints

### Universities API (`/universities`)

#### GET `/universities/filter`

Filter and search universities with optional ranking sorting.

**Query Parameters:**

- `query` (optional): Search term for university name
- `sort_credit` (optional): Ranking table name for sorting (default: "US_News_best global universities_Rankings")
- `country` (optional): Filter by country
- `city` (optional): Filter by city

**Example:**

```bash
curl "http://localhost:10000/universities/filter?query=harvard&country=United%20States"
```

**Response:**

```json
[
  {
    "id": 1,
    "normalized_name": "harvard-university",
    "name": "Harvard University",
    "country": "United States",
    "city": "Cambridge",
    "photo": "harvard.jpg",
    "rank_value": 1,
    "chinese_name": "哈佛大学"
  }
]
```

#### GET `/universities/<int:univ_id>`

Get detailed information about a specific university by ID.

**Example:**

```bash
curl "http://localhost:10000/universities/1"
```

**Response:**

```json
{
  "id": 1,
  "normalized_name": "harvard-university",
  "name": "Harvard University",
  "country": "United States",
  "city": "Cambridge",
  "photo": "harvard.jpg",
  "chinese_name": "哈佛大学",
  "rankings": [
    {
      "subject": "Overall",
      "source": "QS",
      "rank_value": 5
    }
  ],
  "stats": [
    {
      "type": "undergraduate_enrollment",
      "count": 6700,
      "year": 2023
    }
  ]
}
```

#### GET `/universities/<string:name>`

Get university information by normalized name.

**Example:**

```bash
curl "http://localhost:10000/universities/harvard-university"
```

#### GET `/universities/<string:normalized_name>/rankings/<string:source>`

Get university rankings from a specific source.

**Example:**

```bash
curl "http://localhost:10000/universities/harvard-university/rankings/QS"
```

**Response:**

```json
{
  "university": {
    "name": "Harvard University",
    "country": "United States",
    "city": "Cambridge",
    "photo": "harvard.jpg",
    "chinese_name": "哈佛大学"
  },
  "source": "QS",
  "rankings": [
    {
      "subject": "Overall",
      "rank_value": 5
    }
  ]
}
```

#### GET `/universities/translate/<string:normalized_name>`

Get university name in specified language.

**Query Parameters:**

- `language`: Language code (`en` for English, `zh` for Chinese, default: `en`)

**Example:**

```bash
# Get Chinese name
curl "http://localhost:10000/universities/translate/harvard-university?language=zh"

# Get English name
curl "http://localhost:10000/universities/translate/harvard-university?language=en"
```

**Response:**

```json
{
  "normalized_name": "harvard-university",
  "language": "zh",
  "name": "哈佛大学"
}
```

### Dropdown API (`/dropdown`)

#### GET `/dropdown/countries`

Get list of all available countries.

**Example:**

```bash
curl "http://localhost:10000/dropdown/countries"
```

**Response:**

```json
[
  "United States",
  "United Kingdom",
  "Canada"
]
```

#### GET `/dropdown/cities`

Get cities for a specific country.

**Query Parameters:**

- `country`: Country name

**Example:**

```bash
curl "http://localhost:10000/dropdown/cities?country=United%20States"
```

**Response:**

```json
[
  "Cambridge",
  "New York",
  "Berkeley"
]
```

#### GET `/dropdown/ranking_options`

Get available ranking options, optionally filtered by source and subject.

**Query Parameters:**

- `source` (optional): Filter by ranking source
- `subject` (optional): Filter by subject

**Example:**

```bash
# Get all ranking options
curl "http://localhost:10000/dropdown/ranking_options"

# Filter by source
curl "http://localhost:10000/dropdown/ranking_options?source=QS"
```

**Response:**

```json
[
  {
    "table": "QS_World_University_Rankings_2024",
    "source": "QS",
    "subject": "Overall",
    "top_universities": [
      {
        "normalized_name": "harvard-university",
        "rank_value": 5,
        "name": "Harvard University",
        "chinese_name": "哈佛大学"
      }
    ]
  }
]
```

### Subject Rankings API (`/subject_rankings`)

#### GET `/subject_rankings/ranking_detail`

Get detailed ranking information for a specific table, source, and subject.

**Query Parameters:**

- `table`: Ranking table name (required)
- `source`: Ranking source (required)
- `subject`: Ranking subject (required)

**Example:**

```bash
curl "http://localhost:10000/subject_rankings/ranking_detail?table=QS_World_University_Rankings_2024&source=QS&subject=Overall"
```

**Response:**

```json
[
  {
    "normalized_name": "harvard-university",
    "rank_value": 5,
    "name": "Harvard University",
    "chinese_name": "哈佛大学"
  },
  {
    "normalized_name": "stanford-university",
    "rank_value": 6,
    "name": "Stanford University",
    "chinese_name": "斯坦福大学"
  }
]
```

## Database Schema

The application uses SQLite database with the following main tables:

### Universities

- `id`: Primary key
- `normalized_name`: Normalized university name (URL-friendly)
- `name`: Full university name
- `country`: Country location
- `city`: City location
- `photo`: Photo filename

### University_names_en_to_zh

- `id`: Foreign key to Universities.id
- `english_name`: English name
- `chinese_name`: Chinese translation

### Ranking Tables

Dynamic tables for different ranking sources (e.g., `QS_World_University_Rankings_2024`):

- `normalized_name`: Foreign key to Universities.normalized_name
- `source`: Ranking source
- `subject`: Ranking subject/category
- `rank_value`: Numerical ranking

### UniversityStats

- `normalized_name`: Foreign key to Universities.normalized_name
- `type`: Statistic type
- `count`: Statistic value
- `year`: Year of statistic

## Development

### Project Structure

```
University_Ranking_Backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── University_rankings.db # SQLite database
├── models/               # Data models
│   ├── universities.py
│   ├── university.py
│   ├── translations.py
│   ├── ranking_options.py
│   ├── countries.py
│   ├── cities.py
│   └── ranking_options.py
├── routes/               # API route handlers
│   ├── universities.py
│   ├── dropdown.py
│   └── ranking_detail.py
├── scripts/              # Data processing scripts
└── data/                 # Raw data files
```

### Adding New Endpoints

1. Create or modify route handlers in `routes/`
2. Implement business logic in `models/`
3. Register blueprints in `app.py`
4. Update this README

### Data Processing

The `scripts/` directory contains utilities for:

- Processing ranking data from various sources
- Generating translations
- Populating the database

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (missing parameters)
- `404`: Not Found (university or resource not found)

Error responses include a JSON object with an `error` field describing the issue.

## CORS Support

The API includes CORS support for cross-origin requests, making it suitable for web applications.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

```text
Copyright (C) <2025>  <Ruize Xia>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
