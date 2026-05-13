import requests
from django.conf import settings

RAWG_BASE_URL = "https://api.rawg.io/api"


def search_games(query, page=1, page_size=20):
    """Search games on RAWG API"""
    if not getattr(settings, 'RAWG_API_KEY', None):
        return {'error': 'RAWG_API_KEY not configured'}
    
    url = f"{RAWG_BASE_URL}/games"
    params = {
        'key': settings.RAWG_API_KEY,
        'search': query,
        'page': page,
        'page_size': page_size,
        'ordering': '-rating',
    }
    
    try:
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}


def get_game_details(rawg_id):
    """Get detailed game info from RAWG"""
    if not getattr(settings, 'RAWG_API_KEY', None):
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
    """Create Game from RAWG data (improved)"""
    from shop.models import Game
    from decimal import Decimal
    import random
    from datetime import datetime
    
    title = rawg_data.get('name', 'Unknown Game')
    
    # Check if already exists
    existing = Game.objects.filter(title__iexact=title).first()
    if existing:
        return existing, False
    
    description = rawg_data.get('description_raw', '')[:2500] or f"Популярная игра {title}"
    
    developers = rawg_data.get('developers', [])
    developer = developers[0]['name'] if developers else 'Unknown Studio'
    
    publishers = rawg_data.get('publishers', [])
    publisher = publishers[0]['name'] if publishers else developer
    
    released = rawg_data.get('released')
    try:
        release_date = datetime.strptime(released, '%Y-%m-%d').date() if released else datetime.now().date()
    except:
        release_date = datetime.now().date()
    
    genres = rawg_data.get('genres', [])
    genre_slug = genres[0]['slug'] if genres else 'indie'
    genre_map = {'action':'action','adventure':'adventure','rpg':'rpg','strategy':'strategy','shooter':'shooter','indie':'indie','simulation':'simulation','sports':'sports','racing':'racing','puzzle':'puzzle'}
    genre = genre_map.get(genre_slug, 'indie')
    
    price = Decimal(str(round(random.uniform(14.99, 69.99), 2)))
    background_image = rawg_data.get('background_image') or ''
    
    game = Game.objects.create(
        title=title,
        description=description,
        developer=developer,
        publisher=publisher,
        release_date=release_date,
        platform='steam',
        genre=genre,
        price=price,
        image_url=background_image,
        views_count=random.randint(50, 5000),
        sales_count=random.randint(10, 800),
    )
    return game, True
