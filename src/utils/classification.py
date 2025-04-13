"""Classification utilities for the news parser"""

from openai import OpenAI
from tqdm import tqdm

# Import settings from __init__.py
from src.utils import OPENAI_API_KEY
from src.utils.geocoding import extract_location_from_text, get_geocode
from datetime import datetime, timedelta

def classify_news_event(text):
    """
    Classify news event using OpenAI GPT
    
    Args:
        text (str): News title and possibly content
        
    Returns:
        str: Category from predefined list
    """
    if not OPENAI_API_KEY:
        print("Warning: OpenAI API key not set, skipping classification")
        return "Другое"
        
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    CATEGORIES = "Другое, Пожар, ДТП, Кража, Нарушение_порядка, Несчастный_случай"
    FEW_SHOT_EXAMPLES = """
    Примеры классификации:
    Заголовок: "Возгорание сухой травы в парке" → Категория: Пожар
    Заголовок: "Столкновение двух автомобилей на перекрёстке" → Категория: ДТП
    Заголовок: "Ограбление магазина на Ленинском проспекте" → Категория: Кража
    Заголовок: "Пьяная драка у бара 'Рассвет'" → Категория: Нарушение_порядка
    Заголовок: "Падение строительных лесов на прохожего" → Категория: Несчастный_случай
    Заголовок: "Открытие нового сквера в центре" → Категория: Другое
    """
    
    prompt = f"""
    {FEW_SHOT_EXAMPLES}

    Используй только эти категории: {CATEGORIES}

    Заголовок: "{text}" → Категория:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты опытный классификатор происшествий."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=10
        )
        category = response.choices[0].message.content.strip()
        valid_categories = CATEGORIES.split(", ")
        if category not in valid_categories:
            return "Другое"
        return category
    except Exception as e:
        print(f"Error classifying text: {e}")
        return "Другое"

def process_articles_batch(articles_batch):
    """
    Process a batch of articles to enrich with locations, geocodes, and categories
    
    Args:
        articles_batch: List of article dictionaries
        
    Returns:
        List of enriched article dictionaries
    """
    enriched_articles = []
    
    for article in tqdm(articles_batch, desc="Processing articles"):
        # Extract location from text
        combined_text = f"{article['title']} {article['content'][:500]}"
        location = extract_location_from_text(combined_text)
        article['location'] = location
        
        # Get geocode for location
        if location:
            lat, lng = get_geocode(location)
            article['latitude'] = lat
            article['longitude'] = lng
        
        # Classify the news event
        article['category'] = classify_news_event(article['title'])
        
        enriched_articles.append(article)
    
    return enriched_articles