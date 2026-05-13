from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
import json
import random
from shop.utils.rawg_api import search_games, add_game_from_rawg
from shop.models import Game

class AIChatView(View):
    template_name = 'shop/ai_chat.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            msg = data.get('message', '').lower().strip()
            
            if not msg:
                return JsonResponse({'reply': 'Напиши что-нибудь!'})
            
            # === SMART COMMAND PARSING ===
            if any(w in msg for w in ['добавь', 'add', 'найди', 'search', 'покажи']):
                query = msg
                for w in ['добавь', 'add', 'найди', 'search', 'покажи', 'игру', 'game', 'игр']:
                    query = query.replace(w, '').strip()
                if not query: query = 'cyberpunk 2077'
                
                result = search_games(query, page_size=6)
                if result.get('error'):
                    return JsonResponse({'reply': f"Ошибка RAWG: {result['error']}. Проверь RAWG_API_KEY."})
                
                games = result.get('results', [])
                if not games:
                    return JsonResponse({'reply': f'Игры по "{query}" не найдены.'})
                
                added = []
                for g in games[:4]:
                    game, created = add_game_from_rawg(g)
                    if created:
                        added.append(game.title)
                
                if added:
                    return JsonResponse({'reply': f'✅ Добавил в каталог: <b>{", ".join(added)}</b>. Они уже в магазине!'})
                else:
                    return JsonResponse({'reply': 'Игры уже есть в каталоге или не удалось добавить.'})
            
            elif any(w in msg for w in ['покажи', 'list', 'каталог', 'popular', 'популярн']):
                popular = Game.objects.order_by('-sales_count')[:5]
                titles = [g.title for g in popular]
                return JsonResponse({'reply': f'Топ по продажам: <b>{", ".join(titles)}</b>'})
            
            elif 'рекоменд' in msg or 'recommend' in msg:
                recs = Game.objects.order_by('?')[:4]
                return JsonResponse({'reply': 'Рекомендую: ' + ', '.join([g.title for g in recs])})
            
            else:
                replies = [
                    'Я могу добавлять реальные игры из RAWG! Пробуй "добавь Elden Ring"',
                    'Хочешь топ игр? Напиши "покажи популярные"',
                    'Я подключён к RAWG API. Давай добавим что-нибудь крутое!',
                    'Попробуй команды: "добавь новинки", "рекомендуй", "покажи топ"'
                ]
                return JsonResponse({'reply': random.choice(replies)})
        except Exception as e:
            return JsonResponse({'reply': f'Ошибка: {str(e)}'})
