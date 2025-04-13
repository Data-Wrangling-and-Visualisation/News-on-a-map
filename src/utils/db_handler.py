"""Database operations for the news parser"""

import os
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# Import settings from __init__.py
from src.utils import MONGO_URI, MONGO_DB, MONGO_COLLECTION

def save_to_mongodb(articles):
    """
    Save articles to MongoDB
    
    Args:
        articles: List of article dictionaries
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Insert in batches
        batch_size = 100
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i+batch_size]
            collection.insert_many(batch)
            
        print(f"Successfully inserted {len(articles)} articles into MongoDB")
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        # Save to CSV as fallback
        df = pd.DataFrame(articles)
        filename = f"data/news_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved to CSV file: {filename}")