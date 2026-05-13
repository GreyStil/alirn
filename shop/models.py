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
    """ Модель игры """
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
    
    image = models.ImageField(upload_to='games/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)  # For RAWG/external images
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
        """ Текущая цена с учётом скидки """
        if self.discount_percent > 0:
            return self.price * (Decimal('100') - Decimal(self.discount_percent)) / Decimal('100')
        return self.price
    
    @property
    def average_rating(self):
        """ Средняя оценка из отзывов """
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0
        return sum(r.rating for r in reviews) / reviews.count()
    
    @property
    def display_image(self):
        """Return image URL (local or external)"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return 'https://via.placeholder.com/300x200?text=No+Image'
