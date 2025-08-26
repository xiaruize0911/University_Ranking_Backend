# University Ranking Backend

A comprehensive Flask-based REST API for university ranking data aggregation and analysis. This backend service processes and serves ranking data from multiple sources including QS World University Rankings, US News Rankings, and Niche College Rankings.

## 🚀 Features

- **Multi-source Rankings**: Aggregates data from QS, US News, and Niche rankings
- **Subject-specific Rankings**: Supports rankings across hundreds of academic subjects
- **University Profiles**: Detailed university information and statistics
- **RESTful API**: Clean and intuitive endpoints for frontend integration
- **Data Processing**: Automated scripts for ingesting and processing ranking data
- **Flexible Queries**: Support for filtering by source, subject, and university

## 📁 Project Structure

```
University_Ranking_Backend/
├── app.py                 # Flask application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── data/                 # Raw and processed data files
│   ├── niche_college_rankings.json
│   ├── niche_college_rankings_fixed.json
│   └── *.csv files
├── db/                   # Database connection and utilities
│   ├── __init__.py
│   └── database.py
├── models/               # Data models and business logic
│   ├── __init__.py
│   ├── cities.py
│   ├── countries.py
│   ├── ranking_options.py
│   ├── universities.py
│   └── university.py
├── routes/               # API route handlers
│   ├── __init__.py
│   ├── dropdown.py
│   ├── ranking_detail.py
│   └── universities.py
├── scripts/              # Data processing scripts
│   ├── data_to_db_rankings.py
│   ├── data_to_db_stats.py
│   ├── data_to_db_universities.py
│   ├── niche_data_to_db.py
│   ├── QS_subject_data_to_db.py
│   └── QSdata_to_db.py
└── utils/                # Utility functions
    ├── __init__.py
    ├── db_cmd.py
    ├── normalize_name.py
    └── utils.py
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- SQLite3

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/xiaruize0911/University_Ranking_Backend.git
   cd University_Ranking_Backend
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - The SQLite database (`University_rankings.db`) should be included in the repository
   - If you need to rebuild the database, run the data processing scripts:
   ```bash
   python scripts/data_to_db_universities.py
   python scripts/QS_subject_data_to_db.py
   python scripts/niche_data_to_db.py
   ```

## 🚦 Running the Application

### Development Mode
```bash
python app.py
```

The API will be available at `http://localhost:10000`

### Production Mode
For production deployment, consider using a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:10000 app:app
```

## 📚 API Documentation

### Base URL
```
http://localhost:10000
```

### Endpoints

#### 1. Get University Rankings Options
```http
GET /dropdown/ranking_options
```

**Parameters:**
- `source` (optional): Filter by ranking source (QS, USNews, Niche)
- `subject` (optional): Filter by subject area

**Response:**
```json
[
  {
    "table": "QS_Computer_Science_Rankings",
    "source": "QS",
    "subject": "Computer Science",
    "top_universities": [
      {
        "normalized_name": "massachusetts institute of technology",
        "rank_value": 1,
        "name": "Massachusetts Institute of Technology"
      }
    ]
  }
]
```

#### 2. Get Detailed Rankings
```http
GET /subject_rankings/ranking_detail
```

**Parameters:**
- `table` (required): Table name (e.g., "QS_Computer_Science_Rankings")
- `source` (required): Ranking source
- `subject` (required): Subject area

**Response:**
```json
[
  {
    "normalized_name": "massachusetts institute of technology",
    "rank_value": 1,
    "name": "Massachusetts Institute of Technology"
  },
  {
    "normalized_name": "stanford university",
    "rank_value": 2,
    "name": "Stanford University"
  }
]
```

#### 3. Get Universities
```http
GET /universities/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Harvard University",
    "normalized_name": "harvard university",
    "city": "Cambridge",
    "state": "Massachusetts",
    "country": "United States"
  }
]
```

#### 4. Search Universities
```http
GET /universities/search?q=harvard
```

**Parameters:**
- `q` (required): Search query

## 🗄️ Database Schema

### Core Tables

- **universities**: Main university information
- **cities**: City data
- **countries**: Country data
- **{Source}_{Subject}_Rankings**: Individual ranking tables for each source and subject combination

### Ranking Tables
The system automatically creates tables for each ranking source and subject combination:
- `QS_{subject}_Rankings`
- `USNews_{subject}_Rankings`
- `Niche_{subject}_Rankings`

Each ranking table contains:
- `normalized_name`: Standardized university name for joining
- `source`: Ranking provider (QS, USNews, Niche)
- `subject`: Academic subject area
- `rank_value`: Numerical ranking position

## 🔧 Data Processing

### Adding New Ranking Data

1. **QS Rankings**: Place CSV files in the designated directory and run:
   ```bash
   python scripts/QS_subject_data_to_db.py
   ```

2. **Niche Rankings**: Process JSON data:
   ```bash
   python scripts/niche_data_to_db.py
   ```

3. **University Data**: Update main university database:
   ```bash
   python scripts/data_to_db_universities.py
   ```

### Data Sources

- **QS World University Rankings**: Subject-specific rankings
- **US News Rankings**: US university rankings
- **Niche College Rankings**: Comprehensive college rankings across multiple categories

## 🧪 Testing

Test the API endpoints using curl or a tool like Postman:

```bash
# Get ranking options
curl "http://localhost:10000/dropdown/ranking_options"

# Get specific ranking details
curl "http://localhost:10000/subject_rankings/ranking_detail?table=QS_Computer_Science_Rankings&source=QS&subject=Computer Science"

# Search universities
curl "http://localhost:10000/universities/search?q=stanford"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

- Flask: Web framework
- Pandas: Data manipulation and analysis
- Flask-CORS: Cross-Origin Resource Sharing support
- SQLite3: Database (included with Python)

## 🐛 Known Issues

- Large JSON files may require memory optimization for processing
- Some university names may not match perfectly between different ranking sources

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Author

- [GitHub](https://github.com/xiaruize0911)
- [Email](mailto:xiaruize0911@gmail.com)

## 🙏 Acknowledgments

- QS World University Rankings for providing comprehensive university ranking data
- US News & World Report for US university rankings
- Niche.com for detailed college rankings and reviews
- Flask community for excellent documentation and support

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information about the problem
3. Include relevant error messages and steps to reproduce

---


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