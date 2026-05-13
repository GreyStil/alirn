from decimal import Decimal
from django.utils import timezone
from shop.models import Achievement, UserAchievement, UserProfile


def get_or_create_achievement(name, description, points=10, rarity='common', game=None):
    """Helper to get or create achievement safely."""
    achievement, created = Achievement.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'points': points,
            'rarity': rarity,
            'game': game
        }
    )
    return achievement


def award_achievement(user, achievement):
    """Award achievement to user if not already awarded."""
    user_achievement, created = UserAchievement.objects.get_or_create(
        user=user,
        achievement=achievement
    )
    return created


def check_and_award_achievements(user):
    """
    Main function to check and award achievements based on user activity.
    Call this after important actions (purchase, review, top-up).
    """
    if not user.is_authenticated:
        return []

    profile = getattr(user, 'profile', None)
    if not profile:
        return []

    newly_awarded = []

    # === 1. Первая покупка ===
    if user.orders.filter(status__in=['paid', 'completed']).exists():
        achievement = get_or_create_achievement(
            "Первые шаги",
            "Совершите свою первую покупку в магазине.",
            points=10,
            rarity='common'
        )
        if award_achievement(user, achievement):
            newly_awarded.append(achievement)

    # === 2. Коллекционер ===
    owned_count = profile.owned_games.count()

    if owned_count >= 5:
        achievement = get_or_create_achievement(
            "Коллекционер I",
            "Соберите 5 игр в своей библиотеке.",
            points=15,
            rarity='common'
        )
        if award_achievement(user, achievement):
            newly_awarded.append(achievement)

    if owned_count >= 10:
        achievement = get_or_create_achievement(
            "Коллекционер II",
            "Соберите 10 игр в своей библиотеке.",
            points=25,
            rarity='rare'
        )
        if award_achievement(user, achievement):
            newly_awarded.append(achievement)

    if owned_count >= 50:
        achievement = get_or_create_achievement(
            "Коллекционер III",
            "Соберите 50 игр в своей библиотеке.",
            points=50,
            rarity='epic'
        )
        if award_achievement(user, achievement):
            newly_awarded.append(achievement)

    # === 3. Первый отзыв ===
    if user.reviews.exists():
        achievement = get_or_create_achievement(
            "Критик",
            "Напишите свой первый отзыв на игру.",
            points=10,
            rarity='common'
        )
        if award_achievement(user, achievement):
            newly_awarded.append(achievement)

    # === 4. Первое пополнение баланса ===
    if user.balance_topups.exists():
        achievement = get_or_create_achievement(
            "Инвестор",
            "Пополните баланс в первый раз.",
            points=10,
            rarity='common'
        )
        if award_achievement(user, achievement):
            newly_awarded.append(achievement)

    return newly_awarded
