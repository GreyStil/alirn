from django.contrib import admin
from .models import Game, GameKey, Cart, Order, OrderGame, Review, BalanceTopUp, UserProfile


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'developer', 'price', 'discount_percent', 'platform', 'genre', 'sales_count')
    list_filter = ('platform', 'genre', 'created_at')
    search_fields = ('title', 'developer', 'publisher')
    ordering = ('-created_at',)


@admin.register(GameKey)
class GameKeyAdmin(admin.ModelAdmin):
    list_display = ('game', 'key', 'is_used', 'created_at')
    list_filter = ('game', 'is_used', 'created_at')
    search_fields = ('game__title', 'key')
    readonly_fields = ('created_at',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_items_count', 'created_at')
    search_fields = ('user__username',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OrderGame)
class OrderGameAdmin(admin.ModelAdmin):
    list_display = ('order', 'game', 'price_at_purchase')
    search_fields = ('order__id', 'game__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'game')
    search_fields = ('game__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BalanceTopUp)
class BalanceTopUpAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'success', 'created_at')
    list_filter = ('success', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'role', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('role',)
