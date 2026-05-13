from decimal import Decimal
from shop.models import Achievement, UserAchievement


def get_or_create_achievement(name, description, points=10, rarity='common'):
    achievement, created = Achievement.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'points': points,
            'rarity': rarity
        }
    )
    return achievement


def award_achievement(user, achievement):
    obj, created = UserAchievement.objects.get_or_create(
        user=user,
        achievement=achievement
    )
    return created


def check_and_award_achievements(user):
    if not user.is_authenticated:
        return []

    profile = getattr(user, 'profile', None)
    if not profile:
        return []

    newly_awarded = []

    # Первая покупка
    if user.orders.exists():
        ach = get_or_create_achievement("Первые шаги", "Совершите первую покупку", 10, 'common')
        if award_achievement(user, ach):
            newly_awarded.append(ach)

    # Коллекционер
    count = profile.owned_games.count()
    if count >= 5:
        ach = get_or_create_achievement("Коллекционер I", "Соберите 5 игр", 15, 'common')
        if award_achievement(user, ach):
            newly_awarded.append(ach)
    if count >= 10:
        ach = get_or_create_achievement("Коллекционер II", "Соберите 10 игр", 25, 'rare')
        if award_achievement(user, ach):
            newly_awarded.append(ach)
    if count >= 50:
        ach = get_or_create_achievement("Коллекционер III", "Соберите 50 игр", 50, 'epic')
        if award_achievement(user, ach):
            newly_awarded.append(ach)

    # Первый отзыв
    if user.reviews.exists():
        ach = get_or_create_achievement("Критик", "Напишите первый отзыв", 10, 'common')
        if award_achievement(user, ach):
            newly_awarded.append(ach)

    # Первое пополнение
    if user.balance_topups.exists():
        ach = get_or_create_achievement("Инвестор", "Пополните баланс первый раз", 10, 'common')
        if award_achievement(user, ach):
            newly_awarded.append(ach)

    return newly_awarded
