"""Main entry point for the news parser application"""

import os
import concurrent.futures
import pandas as pd
from datetime import datetime

from src.parsers.news_parser import NewsParser
from src.utils.db_handler import save_to_mongodb
from src.utils.classification import process_articles_batch
from src.config.sources import SOURCES_CONFIG

# Configuration
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 4))

def process_source(source_config):
    """Process a single news source and return the results."""
    print(f"\nStarting to parse {source_config['source_name']}...")
    parser = NewsParser(source_config)
    articles = parser.parse_source()
    
    if not articles:
        print(f"No articles found for {source_config['source_name']}")
        return []
    
    print(f"Found {len(articles)} articles for {source_config['source_name']}")
    
    # Convert datetime objects to strings for serialization
    for article in articles:
        if isinstance(article['date'], datetime):
            article['date'] = article['date'].isoformat()
    
    return articles

def main():
    """Main function to run the entire pipeline."""
    print(f"Starting to parse {len(SOURCES_CONFIG)} sources in parallel with {MAX_WORKERS} workers...")
    all_articles = []
    
    # Step 1: Parse all sources in parallel
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(process_source, SOURCES_CONFIG))
        
    # Flatten results
    for result in results:
        all_articles.extend(result)
    
    print(f"Total articles collected: {len(all_articles)}")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save raw articles
    df_raw = pd.DataFrame(all_articles)
    df_raw.to_csv("data/raw_articles.csv", index=False)
    print("Saved raw articles to data/raw_articles.csv")

    # Step 2: Process articles in batches to add locations, geocodes, and categories
    batch_size = 10  # Process in small batches to avoid API rate limits
    processed_articles = []
    
    for i in range(0, len(all_articles), batch_size):
        batch = all_articles[i:i+batch_size]
        enriched_batch = process_articles_batch(batch)
        processed_articles.extend(enriched_batch)
        
    # Save enriched articles
    df_processed = pd.DataFrame(processed_articles)
    df_processed.to_csv("data/processed_articles.csv", index=False)
    print("Saved processed articles to data/processed_articles.csv")
    
    # Step 3: Save to MongoDB
    save_to_mongodb(processed_articles)
    
    print("News processing pipeline completed successfully!")

if __name__ == "__main__":
    main()