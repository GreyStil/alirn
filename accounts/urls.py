from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Аутентификация
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='shop:index'), name='logout'),
    
    # Восстановление пароля
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Профиль
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/orders/', views.OrderListView.as_view(), name='profile_orders'),
    path('profile/library/', views.LibraryView.as_view(), name='profile_library'),
    path('profile/favorites/', views.FavoritesView.as_view(), name='profile_favorites'),
    path('profile/settings/', views.SettingsView.as_view(), name='profile_settings'),
    path('profile/balance/', views.BalanceView.as_view(), name='profile_balance'),
    path('profile/balance/topup/', views.BalanceTopupView.as_view(), name='balance_topup'),
]
