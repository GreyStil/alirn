@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'preferred_currency', 'role')
    list_filter = ('role', 'preferred_currency')
    search_fields = ('user__username', 'user__email')
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Финансы и настройки', {'fields': ('balance', 'preferred_currency')}),
        ('Роль и аватар', {'fields': ('role', 'avatar')}),
    )