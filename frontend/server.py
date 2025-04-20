from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import json
import os
from bson import json_util

# Get environment variables
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB = os.getenv('MONGO_DB', 'news_classification')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'events')

app = Flask(__name__, 
            template_folder='frontend')  # Point to the frontend directory

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

@app.route('/')
def index():
    # Get unique categories for the filter
    categories = collection.distinct('category')
    return render_template('index.html', categories=categories)

@app.route('/api/events')
def get_events():
    # Get filter parameters
    category = request.args.get('category')
    search_text = request.args.get('search')
    
    # Build query
    query = {}
    if category and category != 'all':
        query['category'] = category
    if search_text:
        query['$or'] = [
            {'title': {'$regex': search_text, '$options': 'i'}},
            {'content': {'$regex': search_text, '$options': 'i'}}
        ]
    
    # Execute query
    events = list(collection.find(query))
    
    # Convert MongoDB BSON to JSON
    return json_util.dumps(events)

@app.route('/api/categories')
def get_categories():
    categories = collection.distinct('category')
    return jsonify(categories)

if __name__ == '__main__':
    # Use 0.0.0.0 to make the server accessible outside the container
    app.run(host='0.0.0.0', port=5000, debug=True)