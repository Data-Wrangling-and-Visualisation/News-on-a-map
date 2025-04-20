from pymongo import MongoClient
from datetime import datetime
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['events_db']
collection = db['events']

# Clear existing data
collection.delete_many({})

# Sample categories
categories = [
    "Нарушение_порядка",
    "Криминал",
    "Культура",
    "Политика",
    "Экономика",
    "Спорт",
    "Технологии",
    "Образование"
]

# Sample locations
locations = [
    {"name": "Москва", "lat": 55.7558, "lon": 37.6173},
    {"name": "Санкт-Петербург", "lat": 59.9343, "lon": 30.3351},
    {"name": "Новосибирск", "lat": 55.0084, "lon": 82.9357},
    {"name": "Екатеринбург", "lat": 56.8389, "lon": 60.6057},
    {"name": "Казань", "lat": 55.7887, "lon": 49.1221},
    {"name": "Нью-Йорк", "lat": 40.7128, "lon": -74.0060},
    {"name": "Лондон", "lat": 51.5074, "lon": -0.1278},
    {"name": "Париж", "lat": 48.8566, "lon": 2.3522},
    {"name": "Берлин", "lat": 52.5200, "lon": 13.4050},
    {"name": "Токио", "lat": 35.6762, "lon": 139.6503},
    {"name": "Пекин", "lat": 39.9042, "lon": 116.4074},
    {"name": "Сидней", "lat": -33.8688, "lon": 151.2093},
    {"name": "Рио-де-Жанейро", "lat": -22.9068, "lon": -43.1729},
    {"name": "Кейптаун", "lat": -33.9249, "lon": 18.4241},
    {"name": "Дубай", "lat": 25.2048, "lon": 55.2708},
]

# Sample sources
sources = ["RIAMO", "РБК", "Интерфакс", "ТАСС", "Ведомости", "Коммерсантъ", "CNN", "BBC", "Al Jazeera"]

# Sample titles and content templates
title_templates = [
    "В {city} прошел митинг против нового закона",
    "Полиция {city} задержала подозреваемого в краже",
    "Открытие новой выставки в {city}",
    "Мэр {city} представил бюджет на следующий год",
    "В {city} прошел экономический форум",
    "Команда из {city} выиграла чемпионат страны",
    "В {city} запустили новую технологическую инициативу",
    "Университет {city} открыл новый исследовательский центр"
]

content_templates = [
    "Фото - © «{source}» Подписывайтесь на наш канал: В {city} сегодня прошло масштабное мероприятие, собравшее множество участников...",
    "Фото - © «{source}» По данным нашего источника, в {city} произошло важное событие, которое привлекло внимание общественности...",
    "Фото - © «{source}» Наш корреспондент сообщает из {city} о событии, которое может иметь значительные последствия для региона...",
    "Фото - © «{source}» Эксклюзивный материал из {city}: уникальное событие, которое заставило говорить о себе всю страну..."
]

# Create sample data
sample_data = []

# Generate 100 sample events
for i in range(100):
    location = random.choice(locations)
    category = random.choice(categories)
    source = random.choice(sources)
    
    # Add some randomness to coordinates to spread events
    lat_offset = random.uniform(-0.5, 0.5)
    lon_offset = random.uniform(-0.5, 0.5)
    
    # Create an event
    event = {
        "title": random.choice(title_templates).format(city=location["name"]),
        "date": datetime.now().isoformat(),
        "content": random.choice(content_templates).format(city=location["name"], source=source),
        "url": f"https://{source.lower().replace(' ', '')}.ru/news/{i}",
        "source_name": source,
        "location": f"Место: {location['name']}",
        "latitude": location["lat"] + lat_offset,
        "longitude": location["lon"] + lon_offset,
        "category": category
    }
    
    sample_data.append(event)

# Insert sample data into MongoDB
collection.insert_many(sample_data)

print(f"Successfully created {len(sample_data)} sample events in the database.")
print(f"Categories used: {categories}")