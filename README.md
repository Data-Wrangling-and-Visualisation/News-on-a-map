# News Parser

A comprehensive news parsing application that extracts articles from various Russian news sources, classifies events, extracts location information, and stores data in MongoDB.

## Features

- Multi-source news scraping with Selenium and BeautifulSoup
- Support for both JavaScript-rendered and static pages
- Automatic location extraction using OpenAI GPT
- Geocoding with Yandex Maps API
- News event classification using OpenAI GPT
- Data storage in MongoDB
- Parallel processing for efficient scraping

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Yandex Maps API key (optional for geocoding)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/news-parser.git
cd news-parser