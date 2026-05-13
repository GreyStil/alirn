from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from shop.models import UserProfile, Cart


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создаёт профиль при создании пользователя"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    """Автоматически создаёт корзину при создании пользователя"""
    if created:
        Cart.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль при сохранении пользователя"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
