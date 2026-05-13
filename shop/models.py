from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

GENRE_CHOICES = [('action','Action'),('rpg','RPG'),('adventure','Adventure'),('strategy','Strategy'),('shooter','Shooter'),('puzzle','Puzzle'),('sports','Sports'),('racing','Racing'),('simulation','Simulation'),('indie','Indie')]
PLATFORM_CHOICES = [('steam','Steam'),('epic','Epic Games'),('battle_net','Battle.net'),('gog','GOG'),('uplay','Uplay')]
CURRENCY_CHOICES = [('USD','USD $'),('EUR','EUR €')]
USER_ROLES = [('user','User'),('moderator','Moderator'),('support','Support'),('admin','Admin')]
ORDER_STATUS_CHOICES = [('pending','Pending'),('paid','Paid'),('completed','Completed'),('cancelled','Cancelled')]
TICKET_STATUS = [('open','Open'),('in_progress','In Progress'),('closed','Closed')]

class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    developer = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    release_date = models.DateField()
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.IntegerField(default=0)
    image = models.ImageField(upload_to='games/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)
    sales_count = models.IntegerField(default=0)

    def __str__(self): return self.title
    @property
    def current_price(self):
        if self.discount_percent > 0:
            return self.price * (100 - self.discount_percent) / 100
        return self.price
    def get_price_in_currency(self, currency='USD'):
        return round(self.current_price * (Decimal('0.92') if currency == 'EUR' else 1), 2)
    @property
    def display_image(self):
        return self.image.url if self.image else (self.image_url or 'https://via.placeholder.com/300x200')

class GameKey(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='keys')
    key = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    games = models.ManyToManyField(Game)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='paid')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderGame(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    key = models.OneToOneField(GameKey, on_delete=models.PROTECT)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

class Review(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('game', 'user')
        ordering = ['-created_at']

class BalanceTopUp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balance_topups')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preferred_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='user')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    favorites = models.ManyToManyField(Game, blank=True)
    owned_games = models.ManyToManyField(Game, blank=True)

    def __str__(self): return self.user.username
    @property
    def is_moderator(self): return self.role in ['moderator', 'admin', 'support']
    @property
    def is_support(self): return self.role in ['support', 'admin']
