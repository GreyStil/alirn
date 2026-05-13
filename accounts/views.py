from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from decimal import Decimal
import csv
from django.http import HttpResponse

from shop.models import UserProfile, Cart, Order, BalanceTopUp, OrderGame, Notification


class LoginView(View):
    template_name = 'accounts/login.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect(request.GET.get('next', 'shop:index'))
        messages.error(request, 'Неверное имя пользователя или пароль')
        return render(request, self.template_name)


class RegisterView(View):
    template_name = 'accounts/register.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if not all([username, email, password]):
            messages.error(request, 'Все поля обязательны')
            return render(request, self.template_name)
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, self.template_name)
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, self.template_name)
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, self.template_name)
        
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user)
            Cart.objects.create(user=user)
        messages.success(request, 'Регистрация успешна!')
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['orders_count'] = user.orders.count()
        context['library_count'] = user.profile.owned_games.count()
        context['favorites_count'] = user.profile.favorites.count()
        context['balance'] = user.profile.balance
        context['unread_notifications'] = user.notifications.filter(is_read=False).count()
        context['user_role'] = user.profile.role
        return context


class OrderListView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_orders.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        orders = request.user.orders.all().prefetch_related('order_games__game', 'order_games__key')
        paginator = Paginator(orders, 10)
        page = request.GET.get('page', 1)
        orders_page = paginator.get_page(page)
        return render(request, self.template_name, {'orders': orders_page})


class LibraryView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_library.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        games = request.user.profile.owned_games.all()
        order_games = OrderGame.objects.filter(order__user=request.user, game__in=games).select_related('game', 'key')
        game_keys = {og.game.id: og.key.key for og in order_games}
        paginator = Paginator(games, 12)
        page = request.GET.get('page', 1)
        games_page = paginator.get_page(page)
        return render(request, self.template_name, {'games': games_page, 'game_keys': game_keys})


class MyKeysView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_keys.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        order_games = OrderGame.objects.filter(order__user=request.user).select_related('game', 'key', 'order').order_by('-order__created_at')
        paginator = Paginator(order_games, 20)
        page = request.GET.get('page', 1)
        keys_page = paginator.get_page(page)
        return render(request, self.template_name, {'order_games': keys_page})


class ExportKeysView(LoginRequiredMixin, View):
    login_url = 'accounts:login'
    
    def get(self, request):
        order_games = OrderGame.objects.filter(order__user=request.user).select_related('game', 'key')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="my_keys.csv"'
        writer = csv.writer(response)
        writer.writerow(['Game', 'Key', 'Purchase Date'])
        for og in order_games:
            writer.writerow([og.game.title, og.key.key, og.order.created_at.strftime('%Y-%m-%d %H:%M')])
        return response


class FavoritesView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_favorites.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        games = request.user.profile.favorites.all()
        paginator = Paginator(games, 12)
        page = request.GET.get('page', 1)
        games_page = paginator.get_page(page)
        return render(request, self.template_name, {'games': games_page})


class SettingsView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_settings.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        return render(request, self.template_name, {'current_currency': request.user.profile.preferred_currency})
    
    def post(self, request):
        user = request.user
        profile = user.profile
        
        if 'currency' in request.POST:
            new_currency = request.POST.get('currency')
            if new_currency in ['USD', 'EUR']:
                profile.preferred_currency = new_currency
                profile.save()
                messages.success(request, f'Валюта изменена на {new_currency}')
        
        if 'new_password' in request.POST:
            old = request.POST.get('old_password')
            new = request.POST.get('new_password')
            confirm = request.POST.get('new_password_confirm')
            if not user.check_password(old):
                messages.error(request, 'Неверный текущий пароль')
            elif new != confirm:
                messages.error(request, 'Новые пароли не совпадают')
            else:
                user.set_password(new)
                user.save()
                messages.success(request, 'Пароль изменён')
        
        if 'new_email' in request.POST:
            new_email = request.POST.get('new_email')
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                messages.error(request, 'Этот email уже используется')
            else:
                user.email = new_email
                user.save()
                messages.success(request, 'Email изменён')
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()
            messages.success(request, 'Аватар загружен')
        
        return redirect('accounts:profile_settings')


class BalanceView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_balance.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        profile = request.user.profile
        topups = request.user.balance_topups.all().order_by('-created_at')
        paginator = Paginator(topups, 15)
        page = request.GET.get('page', 1)
        topups_page = paginator.get_page(page)
        return render(request, self.template_name, {'balance': profile.balance, 'topups': topups_page})


class BalanceTopupView(LoginRequiredMixin, View):
    template_name = 'accounts/balance_topup.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        return render(request, self.template_name, {'quick_amounts': [500, 1000, 1500, 2000, 5000]})
    
    def post(self, request):
        try:
            amount = Decimal(request.POST.get('amount'))
            if amount > 0:
                request.session['topup_amount'] = str(amount)
                return redirect('shop:payment_emulate')
            messages.error(request, 'Сумма должна быть больше нуля')
        except:
            messages.error(request, 'Неверная сумма')
        return render(request, self.template_name)
