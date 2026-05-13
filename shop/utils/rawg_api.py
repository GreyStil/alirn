import requests
from django.conf import settings
import random

def search_games(query: str, page: int = 1, page_size: int = 10):
    '''Search games using RAWG API'''
    url = 'https://api.rawg.io/api/games'
    params = {
        'key': settings.RAWG_API_KEY,
        'search': query,
        'page': page,
        'page_size': page_size,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f'RAWG API error: {e}')
        return None

def get_game_details(game_id: int):
    '''Get detailed info about a specific game'''
    url = f'https://api.rawg.io/api/games/{game_id}'
    params = {'key': settings.RAWG_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return None

def add_game_from_rawg(game_data):
    '''Helper to create Game object from RAWG data'''
    from shop.models import Game
    
    if Game.objects.filter(name__iexact=game_data['name']).exists():
        return False
    
    Game.objects.create(
        name=game_data['name'],
        description=game_data.get('description_raw', game_data.get('description', ''))[:1000],
        price=round(random.uniform(9.99, 59.99), 2),
        image_url=game_data.get('background_image', ''),
        genre=', '.join([g['name'] for g in game_data.get('genres', [])][:4]) or 'Action',
        release_date=game_data.get('released')
    )
    return True
