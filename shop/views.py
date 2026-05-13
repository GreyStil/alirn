from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import json

from .models import Game, GameKey, Cart, Order, OrderGame, Review, GENRE_CHOICES, PLATFORM_CHOICES


class IndexView(TemplateView):
    """Главная страница"""
    template_name = 'shop/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Новинки и акции
        context['featured_games'] = Game.objects.filter(discount_percent__gt=0)[:5]
        
        # Популярные игры
        context['popular_games'] = Game.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-sales_count')[:6]
        
        # Случайные рекомендации
        context['recommended_games'] = Game.objects.all().order_by('?')[:6]
        
        return context


class CatalogView(View):
    """Каталог игр с фильтрацией"""
    template_name = 'shop/catalog.html'
    
    def get(self, request):
        games = Game.objects.all()
        
        # Фильтрация по жанру
        genre = request.GET.get('genre', '')
        if genre:
            games = games.filter(genre=genre)
        
        # Фильтрация по платформе
        platform = request.GET.get('platform', '')
        if platform:
            games = games.filter(platform=platform)
        
        # Фильтрация по цене
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        
        if min_price:
            games = games.filter(price__gte=Decimal(min_price))
        if max_price:
            games = games.filter(price__lte=Decimal(max_price))
        
        # Сортировка
        sort = request.GET.get('sort', '-created_at')
        if sort == 'price_asc':
            games = games.order_by('price')
        elif sort == 'price_desc':
            games = games.order_by('-price')
        elif sort == 'popular':
            games = games.order_by('-sales_count')
        elif sort == 'name':
            games = games.order_by('title')
        else:
            games = games.order_by(sort)
        
        # Пагинация
        paginator = Paginator(games, 12)
        page = request.GET.get('page', 1)
        games_page = paginator.get_page(page)
        
        context = {
            'games': games_page,
            'genres': GENRE_CHOICES,
            'platforms': PLATFORM_CHOICES,
            'selected_genre': genre,
            'selected_platform': platform,
            'min_price': min_price,
            'max_price': max_price,
            'sort': sort,
        }
        
        return render(request, self.template_name, context)


class GameDetailView(DetailView):
    """Детальная страница игры"""
    model = Game
    template_name = 'shop/game_detail.html'
    context_object_name = 'game'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.object
        
        # Увеличиваем счётчик просмотров
        game.views_count += 1
        game.save(update_fields=['views_count'])
        
        # Отзывы
        context['reviews'] = game.reviews.all()
        context['average_rating'] = game.average_rating
        context['user_review'] = None
        
        if self.request.user.is_authenticated:
            context['user_review'] = game.reviews.filter(user=self.request.user).first()
            context['is_owned'] = self.request.user.profile.owned_games.filter(id=game.id).exists()
            context['is_favorite'] = self.request.user.profile.favorites.filter(id=game.id).exists()
            context['in_cart'] = self.request.user.cart.games.filter(id=game.id).exists()
        else:
            context['is_owned'] = False
            context['is_favorite'] = False
            context['in_cart'] = False
        
        return context


class CartView(View):
    """Просмотр корзины"""
    template_name = 'shop/cart.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            games = cart.games.all()
        else:
            games = []
            cart = None
        
        context = {
            'cart': cart,
            'games': games,
            'total_price': sum(game.current_price for game in games) if games else 0,
            'items_count': len(games) if games else 0,
        }
        
        return render(request, self.template_name, context)


class AddToCartView(LoginRequiredMixin, View):
    """Добавление игры в корзину"""
    login_url = 'accounts:login'
    
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        cart = request.user.cart
        
        if cart.games.filter(id=game_id).exists():
            messages.warning(request, f'{game.title} уже в корзине')
        else:
            cart.games.add(game)
            messages.success(request, f'{game.title} добавлена в корзину')
        
        return redirect('shop:cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    """Удаление игры из корзины"""
    login_url = 'accounts:login'
    
    def post(self, request, game_id):
        cart = request.user.cart
        game = get_object_or_404(Game, id=game_id)
        
        cart.games.remove(game)
        messages.success(request, f'{game.title} удалена из корзины')
        
        return redirect('shop:cart')


class CheckoutView(LoginRequiredMixin, View):
    """Оформление заказа"""
    template_name = 'shop/checkout.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        cart = request.user.cart
        games = cart.games.all()
        total_price = sum(game.current_price for game in games)
        balance = request.user.profile.balance
        
        if not games:
            messages.error(request, 'Корзина пуста')
            return redirect('shop:cart')
        
        context = {
            'games': games,
            'total_price': total_price,
            'balance': balance,
            'insufficient_balance': balance < total_price,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        cart = request.user.cart
        games = cart.games.all()
        total_price = sum(game.current_price for game in games)
        user_profile = request.user.profile
        
        if not games:
            messages.error(request, 'Корзина пуста')
            return redirect('shop:cart')
        
        if user_profile.balance < total_price:
            messages.error(request, 'Недостаточно средств')
            return redirect('shop:checkout')
        
        # Использование транзакции для безопасности
        with transaction.atomic():
            # Списываем средства
            user_profile.balance -= total_price
            user_profile.save()
            
            # Создаём заказ
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='paid'
            )
            
            # Для каждой игры резервируем ключ
            for game in games:
                # Ищем первый неиспользованный ключ
                key = game.keys.filter(is_used=False).first()
                
                if not key:
                    messages.error(request, f'Нет доступных ключей для {game.title}')
                    return redirect('shop:checkout')
                
                # Помечаем ключ как использованный
                key.is_used = True
                key.save()
                
                # Создаём связь заказ-игра
                OrderGame.objects.create(
                    order=order,
                    game=game,
                    key=key,
                    price_at_purchase=game.current_price
                )
                
                # Увеличиваем счётчик продаж
                game.sales_count += 1
                game.save(update_fields=['sales_count'])
                
                # Добавляем в библиотеку пользователя
                user_profile.owned_games.add(game)
            
            # Очищаем корзину
            cart.games.clear()
        
        messages.success(request, 'Заказ успешно оформлен!')
        return redirect('shop:order_complete', order_id=order.id)


class OrderCompleteView(LoginRequiredMixin, TemplateView):
    """Страница успешного завершения заказа"""
    template_name = 'shop/order_complete.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.GET.get('order_id')
        
        if order_id:
            order = get_object_or_404(Order, id=order_id, user=self.request.user)
            context['order'] = order
            context['order_games'] = order.order_games.all()
        
        return context


class OrderDetailView(LoginRequiredMixin, View):
    """Детали заказа"""
    template_name = 'shop/order_detail.html'
    
    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        order_games = order.order_games.all()
        
        context = {
            'order': order,
            'order_games': order_games,
        }
        
        return render(request, self.template_name, context)


class PaymentEmulateView(LoginRequiredMixin, View):
    """Эмуляция обработки платежа"""
    template_name = 'shop/payment_emulate.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        amount = request.session.get('topup_amount')
        return render(request, self.template_name, {'amount': amount})
    
    def post(self, request):
        amount_str = request.session.get('topup_amount')
        
        if not amount_str:
            messages.error(request, 'Ошибка: сумма не указана')
            return redirect('accounts:balance_topup')
        
        try:
            amount = Decimal(amount_str)
            
            # Пополняем баланс
            with transaction.atomic():
                profile = request.user.profile
                profile.balance += amount
                profile.save()
                
                # Создаём запись о пополнении
                from .models import BalanceTopUp
                BalanceTopUp.objects.create(
                    user=request.user,
                    amount=amount,
                    success=True
                )
            
            # Очищаем сессию
            del request.session['topup_amount']
            if 'topup_user_id' in request.session:
                del request.session['topup_user_id']
            
            messages.success(request, f'Баланс пополнен на {amount} ₽')
            return redirect('accounts:profile_balance')
        
        except Exception as e:
            messages.error(request, f'Ошибка при пополнении баланса: {str(e)}')
            return redirect('accounts:balance_topup')


class AddReviewView(LoginRequiredMixin, View):
    """Добавление отзыва"""
    login_url = 'accounts:login'
    
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        
        # Проверяем, что пользователь купил игру
        if not request.user.profile.owned_games.filter(id=game_id).exists():
            messages.error(request, 'Вы не можете оставить отзыв на игру, которую не купили')
            return redirect('shop:game_detail', pk=game_id)
        
        rating = int(request.POST.get('rating', 3))
        text = request.POST.get('text', '')
        
        review, created = Review.objects.update_or_create(
            game=game,
            user=request.user,
            defaults={
                'rating': rating,
                'text': text,
            }
        )
        
        if created:
            messages.success(request, 'Отзыв добавлен')
        else:
            messages.success(request, 'Отзыв обновлён')
        
        return redirect('shop:game_detail', pk=game_id)


class EditReviewView(LoginRequiredMixin, View):
    """Редактирование отзыва"""
    login_url = 'accounts:login'
    
    def post(self, request, game_id, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user, game_id=game_id)
        
        review.rating = int(request.POST.get('rating', review.rating))
        review.text = request.POST.get('text', review.text)
        review.save()
        
        messages.success(request, 'Отзыв обновлён')
        return redirect('shop:game_detail', pk=game_id)


class DeleteReviewView(LoginRequiredMixin, View):
    """Удаление отзыва"""
    login_url = 'accounts:login'
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        game_id = review.game.id
        review.delete()
        
        messages.success(request, 'Отзыв удалён')
        return redirect('shop:game_detail', pk=game_id)


class SearchView(View):
    """Поиск игр"""
    template_name = 'shop/search.html'
    
    def get(self, request):
        query = request.GET.get('q', '')
        
        if query:
            games = Game.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(developer__icontains=query)
            )
        else:
            games = Game.objects.none()
        
        paginator = Paginator(games, 12)
        page = request.GET.get('page', 1)
        games_page = paginator.get_page(page)
        
        context = {
            'query': query,
            'games': games_page,
        }
        
        return render(request, self.template_name, context)


class AddFavoriteView(LoginRequiredMixin, View):
    """Добавление в избранное"""
    login_url = 'accounts:login'
    
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        profile = request.user.profile
        
        profile.favorites.add(game)
        messages.success(request, f'{game.title} добавлена в избранное')
        
        return redirect('shop:game_detail', pk=game_id)


class RemoveFavoriteView(LoginRequiredMixin, View):
    """Удаление из избранного"""
    login_url = 'accounts:login'
    
    def post(self, request, game_id):
        profile = request.user.profile
        game = get_object_or_404(Game, id=game_id)
        
        profile.favorites.remove(game)
        messages.success(request, f'{game.title} удалена из избранного')
        
        return redirect('shop:game_detail', pk=game_id)
