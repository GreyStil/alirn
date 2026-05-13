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

from shop.models import UserProfile, Cart, Order, BalanceTopUp, OrderGame, Game


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
            
            next_url = request.GET.get('next', 'shop:index')
            return redirect(next_url)
        else:
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
        
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(user=user)
            Cart.objects.create(user=user)
        
        messages.success(request, 'Регистрация успешна! Войдите в систему')
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
        
        return context


class OrderListView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_orders.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        orders = request.user.orders.all().prefetch_related('order_games__game', 'order_games__key')
        
        paginator = Paginator(orders, 10)
        page = request.GET.get('page', 1)
        orders_page = paginator.get_page(page)
        
        context = {'orders': orders_page}
        return render(request, self.template_name, context)


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
        
        context = {'games': games_page, 'game_keys': game_keys}
        return render(request, self.template_name, context)


class MyKeysView(LoginRequiredMixin, View):
    """ Отдельная страница моих ключей """
    template_name = 'accounts/profile_keys.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        order_games = OrderGame.objects.filter(
            order__user=request.user
        ).select_related('game', 'key', 'order').order_by('-order__created_at')
        
        paginator = Paginator(order_games, 20)
        page = request.GET.get('page', 1)
        keys_page = paginator.get_page(page)
        
        context = {'order_games': keys_page}
        return render(request, self.template_name, context)


class FavoritesView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_favorites.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        games = request.user.profile.favorites.all()
        paginator = Paginator(games, 12)
        page = request.GET.get('page', 1)
        games_page = paginator.get_page(page)
        
        context = {'games': games_page}
        return render(request, self.template_name, context)


class SettingsView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_settings.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        user = request.user
        profile = user.profile
        
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
                messages.success(request, 'Пароль успешно изменён')
        
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
        
        return render(request, self.template_name)


class BalanceView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_balance.html'
    login_url = 'accounts:login'
    
    def get(self, request):
        profile = request.user.profile
        topups = request.user.balance_topups.all().order_by('-created_at')
        
        paginator = Paginator(topups, 15)
        page = request.GET.get('page', 1)
        topups_page = paginator.get_page(page)
        
        context = {'balance': profile.balance, 'topups': topups_page}
        return render(request, self.template_name, context)


class BalanceTopupView(LoginRequiredMixin, View):
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
            
            request.session['topup_amount'] = str(amount)
            return redirect('shop:payment_emulate')
        except:
            messages.error(request, 'Неверная сумма')
            return render(request, self.template_name)
