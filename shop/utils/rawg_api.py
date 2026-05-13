import requests
from django.conf import settings
import random
from django.utils import timezone

def search_games(query, page=1, page_size=10):
    '''Search for games using RAWG API'''
    url = 'https://api.rawg.io/api/games'
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
        print(f'RAWG API error: {e}')
        return None

def get_game_details(rawg_id):
    '''Get detailed information about a specific game'''
    url = f'https://api.rawg.io/api/games/{rawg_id}'
    params = {'key': settings.RAWG_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

def add_game_from_rawg(game_data):
    '''Create or update Game model from RAWG data'''
    from shop.models import Game
    
    name = game_data.get('name')
    if not name:
        return None
    
    # Check if game already exists
    if Game.objects.filter(name__iexact=name).exists():
        return Game.objects.get(name__iexact=name)
    
    # Create new game
    game = Game.objects.create(
        name=name,
        description=game_data.get('description_raw', game_data.get('description', ''))[:1000],
        price=round(random.uniform(9.99, 59.99), 2),
        image_url=game_data.get('background_image', ''),
        genre=', '.join([g.get('name') for g in game_data.get('genres', [])][:4]),
        release_date=game_data.get('released'),
        rating=game_data.get('rating', 0),
    )
    return game
