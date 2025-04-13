# **Backend Development Report: News Parser System (Updated)**  

## **1. Introduction**  
We developed a backend system that parses news articles from local news websites, enriches the data using AI classification, **extracts locations using ChatGPT**, **geocodes addresses using Yandex API**, and stores structured data in MongoDB. The system is containerized using Docker and orchestrated with Docker Compose for seamless deployment.  

### **Key Features**  
- **Multi-source news parsing** (4 local news sources)  
- **AI-powered classification** (using ChatGPT API)  
- **Address extraction** (ChatGPT identifies locations from text)  
- **Geocoding** (Yandex API converts addresses to coordinates)  
- **MongoDB storage** with structured schema  
- **Dockerized backend** for easy deployment  
- **Modular & maintainable codebase**  

---

## **2. System Architecture**  

### **2.1. Components**  
1. **News Parser**  
   - Fetches articles from multiple sources  
   - Extracts metadata (`title`, `date`, `content`, `url`, `source_name`)  
2. **Data Enrichment Module**  
   - **ChatGPT Classification**: Labels articles into predefined categories  
   - **Address Extraction**: ChatGPT identifies locations from article text  
   - **Geocoding**: Yandex API converts locations to `latitude`/`longitude`  
3. **Database Storage**  
   - MongoDB stores enriched articles with schema:  
     ```json
     {
       "title": String,
       "date": ISODate,
       "content": String,
       "url": String,
       "source_name": String,
       "location": String,       // Extracted address (e.g., "ул. Ленина, 10")
       "latitude": Float,       // Yandex-geocoded  
       "longitude": Float,      // Yandex-geocoded  
       "category": String       // ChatGPT-labeled (e.g., "Пожар")
     }
     ```
4. **Docker & Docker Compose**  
   - Backend service (`news-parser`)  
   - MongoDB service (`mongodb`)  

### **2.2. Data Flow**  
1. **Parsing** → Fetch raw articles  
2. **Enrichment** →  
   - ChatGPT classifies articles (`category`)  
   - ChatGPT extracts locations (`location`)  
   - Yandex API geocodes locations (`latitude`, `longitude`)  
3. **Storage** → Saved to MongoDB  
4. **Backup** → CSV export (`/data/processed_articles.csv`)  

---

## **3. Implementation Details**  

### **3.1. News Parsing**  
- **Sources**: 4 local news websites (configurable in `src/config/sources.py`)  
- **Parallel Processing**: Uses `concurrent.futures` for efficiency  

### **3.2. AI Enrichment (ChatGPT API)**  
- **Classification Categories**:  
  ```plaintext
  Другое | Пожар | ДТП | Кража | Нарушение_порядка | Несчастный_случай  
  ```
- **Address Extraction**:  
  - Prompt: *"Extract the exact location mentioned in this article (e.g., 'ул. Ленина, 10'). Return only the address or 'N/A'."*  
  - Example output: `"пр. Мира, 25"`  
- **Batch Processing**: Processes in batches of 10 to avoid API rate limits.  

### **3.3. Geocoding (Yandex API)**  
- **Input**: Raw address from ChatGPT (e.g., `"ул. Советская, 5"`)  
- **Output**:  
  ```json
  { "latitude": 56.12345, "longitude": 44.56789 }  
  ```
- **Error Handling**: Skips failed geocoding; logs errors.  

### **3.4. Database & Storage**  
- **MongoDB Operations** (via `src/utils/db_handler.py`):  
  ```python
  def save_to_mongodb(articles):
      try:
          client = MongoClient(MONGO_URI)
          db = client[MONGO_DB]
          collection = db[MONGO_COLLECTION]
          
          # Insert in batches (100 articles/batch)
          for i in range(0, len(articles), 100):
              collection.insert_many(articles[i:i+100])
          
          print(f"Inserted {len(articles)} articles into MongoDB")
      except Exception as e:
          print(f"MongoDB save failed: {e}")
          # Fallback to CSV
          pd.DataFrame(articles).to_csv(f"data/backup_{datetime.now()}.csv")
  ```
- **Data Columns** (processed):  
  | Field | Type | Description |  
  |-------|------|-------------|  
  | `title` | String | Article headline |  
  | `date` | ISODate | Publication date |  
  | `content` | String | Full article text |  
  | `url` | String | Source URL |  
  | `source_name` | String | News website name |  
  | `location` | String | Extracted address |  
  | `latitude` | Float | Yandex geocoded |  
  | `longitude` | Float | Yandex geocoded |  
  | `category` | String | ChatGPT classification |  

### **3.5. Dockerization**  
- **Dockerfile**:  
  - Installs Chrome (for JS-rendered sites)  
  - Non-root user (`appuser`) for security  
- **Docker Compose**:  
  ```yaml
  services:
    news-parser:
      environment:
        - OPENAI_API_KEY=xxx       # For ChatGPT
        - YANDEX_API_KEY=xxx       # For geocoding
        - MONGO_URI=mongodb://mongodb:27017/
    mongodb:
      image: mongo:6.0
      volumes:
        - mongodb_data:/data/db    # Persistent storage
  ```

---

## **4. Future Improvements**  
- **Geocoding Cache**: Store addresses → coordinates to avoid duplicate API calls.  
- **Better Location Parsing**: Use NER (Named Entity Recognition) for more precise extraction.  
- **Scheduled Runs**: Cron job for daily updates.  

