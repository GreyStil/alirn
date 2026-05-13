from django.urls import path
from . import views
from .ai_views import AIChatView

app_name = 'shop'

urlpatterns = [
    # Главная страница
    path('', views.IndexView.as_view(), name='index'),
    
    # Каталог
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    
    # Детали игры
    path('game/<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    
    # Корзина
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:game_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:game_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    
    # Оформление заказа
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/complete/<int:order_id>/', views.OrderCompleteView.as_view(), name='order_complete'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # Оплата (эмуляция)
    path('payment/emulate/', views.PaymentEmulateView.as_view(), name='payment_emulate'),
    
    # Отзывы
    path('game/<int:game_id>/review/add/', views.AddReviewView.as_view(), name='add_review'),
    path('game/<int:game_id>/review/edit/<int:review_id>/', views.EditReviewView.as_view(), name='edit_review'),
    path('review/delete/<int:review_id>/', views.DeleteReviewView.as_view(), name='delete_review'),
    
    # Поиск
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Избранное
    path('favorites/add/<int:game_id>/', views.AddFavoriteView.as_view(), name='add_favorite'),
    path('favorites/remove/<int:game_id>/', views.RemoveFavoriteView.as_view(), name='remove_favorite'),
    
    # AI Ассистент (RAWG real-time games)
    path('ai-chat/', AIChatView.as_view(), name='ai_chat'),
]