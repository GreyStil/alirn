from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import F
from decimal import Decimal
from .models import Game, GameKey, Cart, Order, OrderGame, Review, BalanceTopUp, UserProfile


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'developer', 'price', 'discount_percent', 'platform', 'genre', 'sales_count')
    list_filter = ('platform', 'genre', 'created_at')
    search_fields = ('title', 'developer', 'publisher')
    ordering = ('-created_at',)


@admin.register(GameKey)
class GameKeyAdmin(admin.ModelAdmin):
    list_display = ('game', 'key', 'is_used')
    list_filter = ('game', 'is_used')
    search_fields = ('game__title', 'key')

    actions = ['mark_as_used', 'mark_as_unused']

    @admin.action(description='Пометить как использованные')
    def mark_as_used(self, request, queryset):
        updated = queryset.update(is_used=True)
        self.message_user(request, f'{updated} ключей помечены как использованные.')

    @admin.action(description='Пометить как неиспользованные')
    def mark_as_unused(self, request, queryset):
        updated = queryset.update(is_used=False)
        self.message_user(request, f'{updated} ключей помечены как неиспользованные.')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)

    actions = ['mark_as_completed', 'mark_as_cancelled']

    @admin.action(description='Пометить как выполненные')
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} заказов помечены как выполненные.')

    @admin.action(description='Отменить заказы')
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} заказов отменены.')


@admin.register(OrderGame)
class OrderGameAdmin(admin.ModelAdmin):
    list_display = ('order', 'game', 'price_at_purchase')
    search_fields = ('order__id', 'game__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'game')
    search_fields = ('game__title', 'user__username')
    readonly_fields = ('created_at',)

    actions = ['approve_reviews', 'hide_reviews']

    @admin.action(description='Одобрить отзывы')
    def approve_reviews(self, request, queryset):
        # Можно добавить поле is_approved в модель при необходимости
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} отзывов одобрено.')

    @admin.action(description='Скрыть отзывы')
    def hide_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} отзывов скрыто.')


@admin.register(BalanceTopUp)
class BalanceTopUpAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    fk_name = 'user'
    fields = ('balance', 'preferred_currency', 'role', 'avatar')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'preferred_currency', 'role', 'created_at')
    list_filter = ('role', 'preferred_currency')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Финансы и настройки', {'fields': ('balance', 'preferred_currency')}),
        ('Роль и аватар', {'fields': ('role', 'avatar')}),
    )

    actions = ['add_balance_1000', 'make_moderator', 'make_regular_user', 'reset_balance']

    @admin.action(description='Пополнить баланс на 1000')
    def add_balance_1000(self, request, queryset):
        for profile in queryset:
            profile.balance += Decimal('1000.00')
            profile.save()
        self.message_user(request, f'Баланс пополнен на 1000 у {queryset.count()} пользователей.')

    @admin.action(description='Сделать модератором')
    def make_moderator(self, request, queryset):
        updated = queryset.update(role='moderator')
        self.message_user(request, f'{updated} пользователей стали модераторами.')

    @admin.action(description='Сделать обычным пользователем')
    def make_regular_user(self, request, queryset):
        updated = queryset.update(role='user')
        self.message_user(request, f'{updated} пользователей стали обычными пользователями.')

    @admin.action(description='Сбросить баланс до 0')
    def reset_balance(self, request, queryset):
        updated = queryset.update(balance=Decimal('0.00'))
        self.message_user(request, f'Баланс сброшен у {updated} пользователей.')


# Перерегистрируем стандартную модель User с Inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)