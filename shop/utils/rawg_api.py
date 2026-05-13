import requests
from django.conf import settings

RAWG_BASE_URL = "https://api.rawg.io/api"


def search_games(query, page=1, page_size=20):
    """Search games on RAWG API"""
    if not settings.RAWG_API_KEY:
        return None
    
    url = f"{RAWG_BASE_URL}/games"
    params = {
        'key': settings.RAWG_API_KEY,
        'search': query,
        'page': page,
        'page_size': page_size,
        'ordering': '-rating',
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"RAWG search error: {e}")
        return None


def get_game_details(rawg_id):
    """Get detailed game info from RAWG"""
    if not settings.RAWG_API_KEY:
        return None
        
    url = f"{RAWG_BASE_URL}/games/{rawg_id}"
    params = {'key': settings.RAWG_API_KEY}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"RAWG details error: {e}")
        return None


def add_game_from_rawg(rawg_data):
    """Create or update Game from RAWG data"""
    from shop.models import Game
    from decimal import Decimal
    import random
    from datetime import datetime
    
    title = rawg_data.get('name', 'Unknown Game')
    
    # Check if game already exists
    existing = Game.objects.filter(title__iexact=title).first()
    if existing:
        return existing, False
    
    # Get description
    description = rawg_data.get('description_raw', rawg_data.get('description', ''))[:2000]
    if not description:
        description = f"Popular game: {title}"
    
    # Developer/Publisher
    developers = rawg_data.get('developers', [])
    developer = developers[0]['name'] if developers else 'Unknown'
    
    publishers = rawg_data.get('publishers', [])
    publisher = publishers[0]['name'] if publishers else developer
    
    # Release date
    released = rawg_data.get('released')
    if released:
        try:
            release_date = datetime.strptime(released, '%Y-%m-%d').date()
        except:
            release_date = datetime.now().date()
    else:
        release_date = datetime.now().date()
    
    # Genre
    genres = rawg_data.get('genres', [])
    genre = genres[0]['slug'] if genres else 'indie'
    # Map to our choices
    genre_map = {
        'action': 'action', 'adventure': 'adventure', 'rpg': 'rpg',
        'strategy': 'strategy', 'shooter': 'shooter', 'indie': 'indie',
        'simulation': 'simulation', 'sports': 'sports', 'racing': 'racing',
        'puzzle': 'puzzle'
    }
    genre = genre_map.get(genre, 'indie')
    
    # Platform - default to steam
    platform = 'steam'
    
    # Price - random reasonable price
    price = Decimal(str(round(random.uniform(9.99, 59.99), 2)))
    
    # Image
    background_image = rawg_data.get('background_image') or ''
    
    game = Game.objects.create(
        title=title,
        description=description,
        developer=developer,
        publisher=publisher,
        release_date=release_date,
        platform=platform,
        genre=genre,
        price=price,
        image=background_image,  # Will use URL or handle in template
        views_count=0,
        sales_count=0,
    )
    
    return game, True
