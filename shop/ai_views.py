from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import random

from shop.utils.rawg_api import search_games, get_game_details, add_game_from_rawg
from shop.models import Game


class AIChatView(View):
    """AI Assistant chat for searching and adding real games from RAWG"""
    template_name = 'shop/ai_chat.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip().lower()
            
            if not user_message:
                return JsonResponse({'reply': 'Напиши что-нибудь!'})
            
            # Check for add game intent
            if any(word in user_message for word in ['добавь', 'add', 'найди', 'search', 'покажи']):
                # Extract game name (simple heuristic)
                query = user_message
                for word in ['добавь', 'add', 'найди', 'search', 'покажи', 'игру', 'game']:
                    query = query.replace(word, '').strip()
                
                if not query:
                    query = 'cyberpunk'  # default example
                
                rawg_data = search_games(query, page_size=5)
                
                if rawg_data and rawg_data.get('results'):
                    added_games = []
                    for game_data in rawg_data['results'][:3]:  # Add up to 3
                        game, created = add_game_from_rawg(game_data)
                        if created:
                            added_games.append(game.title)
                    
                    if added_games:
                        reply = f'Добавил в каталог: {", ".join(added_games)}. Теперь они доступны в магазине!'
                    else:
                        reply = 'Игры уже есть в каталоге или не найдены.'
                else:
                    reply = 'Не удалось найти игры по запросу. Попробуй другое название.'
            else:
                # General chat response
                reply = self._get_general_response(user_message)
            
            return JsonResponse({'reply': reply})
        
        except Exception as e:
            return JsonResponse({'reply': f'Ошибка: {str(e)}'})
    
    def _get_general_response(self, message):
        responses = [
            'Я могу помочь добавить реальные игры из RAWG в каталог!',
            'Напиши "добавь Cyberpunk 2077" или "найди RPG 2024", и я добавлю их!',
            'Хочешь свежие игры? Просто скажи что добавить.',
            'Я интегрирован с RAWG API для реальных данных.',
        ]
        return random.choice(responses)
