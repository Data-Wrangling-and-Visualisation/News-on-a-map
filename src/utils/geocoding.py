"""Geocoding utilities for the news parser"""

import requests
from openai import OpenAI

# Import settings from __init__.py
from src.utils import OPENAI_API_KEY, YANDEX_API_KEY

def extract_location_from_text(text):
    """
    Use OpenAI GPT to extract location information from news text
    
    Args:
        text (str): News title and content
        
    Returns:
        str: Location string or None if no location found
    """
    if not OPENAI_API_KEY:
        print("Warning: OpenAI API key not set, skipping location extraction")
        return None
        
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""
    Извлеки географическое место из новостного текста. Верни только адрес или место происшествия 
    (например, "ул. Ленина, Москва", "ТЦ Мега, Химки", "МКАД, 32-й километр").
    Если места нет в тексте, верни "Unknown".
    
    Текст: {text[:1000]}  # Limiting text length
    
    Место: 
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - система извлечения мест из текста."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=50
        )
        location = response.choices[0].message.content.strip()
        return None if location == "Unknown" else location
    except Exception as e:
        print(f"Error extracting location: {e}")
        return None


def get_geocode(address):
    """
    Geocode an address using Yandex Maps API
    
    Args:
        address (str): Address to geocode
        
    Returns:
        tuple: (latitude, longitude) or (None, None) if geocoding fails
    """
    if not address:
        return None, None
        
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        'apikey': YANDEX_API_KEY,
        'geocode': address,
        'lang': 'ru_RU',
        'format': 'json',
        'results': 1
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        result = response.json()
        
        try:
            pos = result['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            longitude, latitude = pos.split()
            return float(latitude), float(longitude)
        except (KeyError, IndexError):
            return None, None
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
        return None, None