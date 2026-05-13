from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Жанры и платформы (выборы)
GENRE_CHOICES = [
    ('action', 'Action'),
    ('rpg', 'RPG'),
    ('adventure', 'Adventure'),
    ('strategy', 'Strategy'),
    ('shooter', 'Shooter'),
    ('puzzle', 'Puzzle'),
    ('sports', 'Sports'),
    ('racing', 'Racing'),
    ('simulation', 'Simulation'),
    ('indie', 'Indie'),
]

PLATFORM_CHOICES = [
    ('steam', 'Steam'),
    ('epic', 'Epic Games'),
    ('battle_net', 'Battle.net'),
    ('gog', 'GOG'),
    ('uplay', 'Uplay'),
]

ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]


class Game(models.Model):
    """Модель игры"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    developer = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    release_date = models.DateField()
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    region = models.CharField(max_length=100, default='Global')
    system_requirements = models.TextField(blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount_percent = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    image = models.ImageField(upload_to='games/')
    cover_image = models.ImageField(upload_to='games/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    views_count = models.IntegerField(default=0)
    sales_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def current_price(self):
        """Текущая цена с учётом скидки"""
        if self.discount_percent > 0:
            return self.price * (Decimal('100') - Decimal(self.discount_percent)) / Decimal('100')
        return self.price
    
    @property
    def average_rating(self):
        """Средняя оценка из отзывов"""
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0
        return sum(r.rating for r in reviews) / reviews.count()


class GameKey(models.Model):
    """Модель ключа активации игры"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='keys')
    key = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Game Keys'
    
    def __str__(self):
        return f'{self.game.title} - {self.key[:10]}...'


class Cart(models.Model):
    """Модель корзины"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    games = models.ManyToManyField(Game, related_name='in_carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Cart of {self.user.username}'
    
    @property
    def total_price(self):
        """Общая стоимость товаров в корзине"""
        return sum(game.current_price for game in self.games.all())
    
    def get_items_count(self):
        """Количество товаров в корзине"""
        return self.games.count()


class Order(models.Model):
    """Модель заказа"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    games = models.ManyToManyField(Game, through='OrderGame')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Order #{self.id} - {self.user.username}'


class OrderGame(models.Model):
    """Связь между заказом и игрой с ключом"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    key = models.OneToOneField(GameKey, on_delete=models.PROTECT, related_name='order_game')
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'{self.order} - {self.game.title}'


class Review(models.Model):
    """Модель отзыва на игру"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('game', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.game.title} ({self.rating}★)'


class BalanceTopUp(models.Model):
    """Модель пополнения баланса"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balance_topups')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Balance TopUps'
    
    def __str__(self):
        return f'{self.user.username} - {self.amount}'


class Promocode(models.Model):
    """Модель промокода"""
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=[('percent', 'Percent'), ('fixed', 'Fixed')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_usage = models.IntegerField(null=True, blank=True)
    current_usage = models.IntegerField(default=0)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.code


class UserProfile(models.Model):
    """Расширенный профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.png')
    favorites = models.ManyToManyField(Game, related_name='favorited_by', blank=True)
    owned_games = models.ManyToManyField(Game, related_name='owned_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username
