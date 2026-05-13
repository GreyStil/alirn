from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from decimal import Decimal

from shop.models import UserProfile, Cart, Order, BalanceTopUp


class LoginView(View):
    """Вход в систему"""
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
            
            next_url = request.GET.get('next', 'shop:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
            return render(request, self.template_name)


class RegisterView(View):
    """Регистрация"""
    template_name = 'accounts/register.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Валидация
        if not username or not email or not password:
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
        
        # Создание пользователя
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Создание профиля
            UserProfile.objects.create(user=user)
            
            # Создание корзины
            Cart.objects.create(user=user)
        
        messages.success(request, 'Регистрация успешна! Войдите в систему')
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Главная страница профиля"""
    template_name = 'accounts/profile.html'
    login_url = 'accounts:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['orders_count'] = user.orders.count()
        context['library_count'] = user.profile.owned_games.count()
        context['favorites_count'] = user.profile.favorites.count()
        context['balance'] = user.profile.balance
        
        return context


class OrderListView(LoginRequiredMixin, View):
    """Список заказов"""
    template_name = 'accounts/profile_orders.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        orders = request.user.orders.all()
        
        paginator = Paginator(orders, 10)
        page = request.GET.get('page', 1)
        orders_page = paginator.get_page(page)
        
        context = {
            'orders': orders_page,
        }
        
        return render(request, self.template_name, context)


class LibraryView(LoginRequiredMixin, View):
    """Библиотека игр"""
    template_name = 'accounts/profile_library.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        games = request.user.profile.owned_games.all()
        
        paginator = Paginator(games, 12)
        page = request.GET.get('page', 1)
        games_page = paginator.get_page(page)
        
        context = {
            'games': games_page,
        }
        
        return render(request, self.template_name, context)


class FavoritesView(LoginRequiredMixin, View):
    """Избранное"""
    template_name = 'accounts/profile_favorites.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        games = request.user.profile.favorites.all()
        
        paginator = Paginator(games, 12)
        page = request.GET.get('page', 1)
        games_page = paginator.get_page(page)
        
        context = {
            'games': games_page,
        }
        
        return render(request, self.template_name, context)


class SettingsView(LoginRequiredMixin, View):
    """Настройки профиля"""
    template_name = 'accounts/profile_settings.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        user = request.user
        profile = user.profile
        
        # Изменение пароля
        if 'new_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            new_password_confirm = request.POST.get('new_password_confirm')
            
            if not user.check_password(old_password):
                messages.error(request, 'Неверный текущий пароль')
            elif new_password != new_password_confirm:
                messages.error(request, 'Новые пароли не совпадают')
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Пароль изменён')
        
        # Изменение email
        if 'new_email' in request.POST:
            new_email = request.POST.get('new_email')
            
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                messages.error(request, 'Этот email уже используется')
            else:
                user.email = new_email
                user.save()
                messages.success(request, 'Email изменён')
        
        # Загрузка аватара
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()
            messages.success(request, 'Аватар загружен')
        
        return render(request, self.template_name)


class BalanceView(LoginRequiredMixin, View):
    """Просмотр баланса"""
    template_name = 'accounts/profile_balance.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        profile = request.user.profile
        topups = request.user.balance_topups.all()
        
        paginator = Paginator(topups, 20)
        page = request.GET.get('page', 1)
        topups_page = paginator.get_page(page)
        
        context = {
            'balance': profile.balance,
            'topups': topups_page,
        }
        
        return render(request, self.template_name, context)


class BalanceTopupView(LoginRequiredMixin, View):
    """Пополнение баланса"""
    template_name = 'accounts/balance_topup.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        amount_str = request.POST.get('amount')
        
        try:
            amount = Decimal(amount_str)
            
            if amount <= 0:
                messages.error(request, 'Сумма должна быть больше нуля')
                return render(request, self.template_name)
            
            # Сохраняем сумму в сессии для эмуляции платежа
            request.session['topup_amount'] = str(amount)
            request.session['topup_user_id'] = request.user.id
            
            # Перенаправляем на страницу эмуляции платежа
            return redirect('shop:payment_emulate')
        
        except (ValueError, Decimal.InvalidOperation):
            messages.error(request, 'Неверная сумма')
            return render(request, self.template_name)
