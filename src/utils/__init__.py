"""Utils package initialization"""

import os
import datetime

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY", "")

# MongoDB settings
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.environ.get("MONGO_DB", "news_classification")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "events")