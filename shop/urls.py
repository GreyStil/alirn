from django.urls import path
from . import views
from .ai_views import AIChatView

app_name = 'shop'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('game/<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:game_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:game_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order-complete/', views.OrderCompleteView.as_view(), name='order_complete'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('ai-chat/', AIChatView.as_view(), name='ai_chat'),
    
    # Moderator
    path('moderator/reviews/', views.ModeratorReviewsView.as_view(), name='moderator_reviews'),
    path('moderator/reviews/delete/<int:review_id>/', views.DeleteReviewModeratorView.as_view(), name='moderator_delete_review'),
    
    # Tickets
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/create/', views.CreateTicketView.as_view(), name='create_ticket'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
]