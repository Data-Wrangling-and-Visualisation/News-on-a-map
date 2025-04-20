# News Parser

A comprehensive news parsing application that extracts articles from various Russian news sources, classifies events, extracts location information, and stores data in MongoDB. The application includes a web-based visualization component to display news events on an interactive map.

## Features

- **Multi-source news scraping** with Selenium and BeautifulSoup
- Support for both JavaScript-rendered and static pages
- **Automatic location extraction** using OpenAI GPT
- **Geocoding** with Yandex Maps API
- **News event classification** using OpenAI GPT
- **Data storage** in MongoDB
- **Parallel processing** for efficient scraping
- **Interactive map visualization** of news events

## Project Structure

```
news-parser/
├── .env                         # Environment variables
├── .gitkeep                     # Git placeholder
├── .gitignore                   # Git ignore file
├── README.md                    # Project documentation
├── Dockerfile                   # Main application Docker configuration
├── Dockerfile.frontend          # Frontend Docker configuration
├── docker-compose.yml           # Docker Compose configuration
├── requirements.txt             # Python dependencies for main app
├── requirements.frontend.txt    # Python dependencies for frontend
├── backend_parsing_template.ipynb # Jupyter notebook template for parsing
├── data/
│   ├── .gitkeep                 # Git placeholder
│   ├── processed_articles.csv   # Processed news articles
│   └── raw_articles.csv         # Raw scraped articles
├── frontend/
│   ├── index.html               # Main web interface
│   ├── make_sample.py           # Sample data generator for frontend
│   └── server.py                # Frontend web server
├── reports_and_documents/
│   ├── documents_backend_stage/
│   │   └── Report.md            # Backend development reports
│   └── documents_planning/
│       ├── data_flow.svg        # Data flow diagram
│       ├── detailed.svg         # Detailed architecture diagram
│       ├── high-level.svg       # High-level architecture diagram
│       ├── initial_work.ipynb   # Initial project planning notebook
│       ├── mongodb_arch.svg     # MongoDB architecture diagram
│       └── Regional News Sources.pdf # Documentation of news sources
├── src/
│   ├── __init__.py              # Package initializer
│   ├── main.py                  # Main application entry point
│   ├── config/
│   │   ├── __init__.py          # Config package initializer
│   │   └── sources.py           # News sources configuration
│   ├── parsers/
│   │   ├── __init__.py          # Parsers package initializer
│   │   ├── base_parser.py       # Base parser class
│   │   └── news_parser.py       # News parser implementation
│   └── utils/
│       └── __init__.py          # Utilities package initializer
└── tests/                       # Test directory
```

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Yandex Maps API key (for geocoding)
- Mapbox API key (for frontend map visualization)

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/news-parser.git
   cd news-parser
   ```

2. **Create environment variables file:**
   Create a `.env` file in the root directory with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   YANDEX_API_KEY=your_yandex_api_key
   MONGO_URI=mongodb://mongodb:27017/
   MONGO_DB=news_classification
   MONGO_COLLECTION=events
   MAX_WORKERS=4
   ```

3. **Set up Mapbox API key:**
   You need to obtain a Mapbox API key from [Mapbox](https://account.mapbox.com/auth/signup/) to enable the map visualization.

   Open the file `frontend/index.html` and locate the following line:
   ```javascript
   mapboxgl.accessToken = 'pk...';
   ```
   
   Replace the token value with your own Mapbox access token. The line should look like:
   ```javascript
   mapboxgl.accessToken = 'your_mapbox_access_token';
   ```

4. **Build and start the application using Docker Compose:**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

## Running the Application

### Backend Parser

The backend parser will run automatically when you start the Docker containers. It:
- Scrapes news from configured sources
- Processes and extracts relevant information
- Classifies news events
- Extracts and geocodes locations
- Stores the data in MongoDB

To check logs:
```bash
docker-compose logs -f news-parser
```

### Frontend Map Visualization

Access the news visualization map in your browser:
```
http://localhost:5000
```

The map provides:
- Visual representation of news events on a world map
- Filtering by news category
- Search functionality
- Detailed news information on click

#### Map Features

The interactive map uses Mapbox GL JS to display news events with the following capabilities:
- Zoom in to see more detailed geographical features (towns, streets, buildings)
- Hover over markers to view brief information about the news event
- Click on markers to open detailed news articles
- Filter news events by category or search text
- Color-coded markers based on event categories

## Development

### Extending the News Sources

To add more news sources, modify the `src/config/sources.py` file:

```python
NEWS_SOURCES = [
    {
        "name": "Source Name",
        "url": "https://source-url.com",
        "selector": "article selector",
        "requires_js": True/False
    },
    # Add more sources here
]
```

### Creating a Custom Parser

1. Create a new file in the `src/parsers` directory
2. Extend the `BaseParser` class from `base_parser.py`
3. Implement the required methods
4. Register your parser in the main application

Example:
```python
from src.parsers.base_parser import BaseParser

class CustomParser(BaseParser):
    def __init__(self, config):
        super().__init__(config)
    
    def parse(self, url):
        # Implement your parsing logic
        pass
```

## Testing

Run tests using:
```bash
docker-compose exec news-parser python -m pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
