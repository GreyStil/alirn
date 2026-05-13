from django.shortcuts import render, redirect, get_object_or_create
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# ... остальные импорты ...

from shop.utils.achievements import check_and_award_achievements, get_or_create_achievement

# ... существующий код ...

class ProfileAchievementsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile_achievements.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Получаем все достижения пользователя
        user_achievements = user.achievements.select_related('achievement').all().order_by('-unlocked_at')
        unlocked_ids = set(user_achievements.values_list('achievement_id', flat=True))

        # Создаём базовые достижения, если их ещё нет
        default_achievements = [
            ("Первые шаги", "Совершите свою первую покупку в магазине.", 10, 'common'),
            ("Коллекционер I", "Соберите 5 игр в своей библиотеке.", 15, 'common'),
            ("Коллекционер II", "Соберите 10 игр в своей библиотеке.", 25, 'rare'),
            ("Коллекционер III", "Соберите 50 игр в своей библиотеке.", 50, 'epic'),
            ("Критик", "Напишите свой первый отзыв на игру.", 10, 'common'),
            ("Инвестор", "Пополните баланс в первый раз.", 10, 'common'),
            ("Отзывчивый", "Напишите 5 отзывов.", 20, 'rare'),
        ]

        for name, desc, points, rarity in default_achievements:
            get_or_create_achievement(name, desc, points, rarity)

        # Все достижения
        all_achievements = Achievement.objects.all().order_by('rarity', 'points')

        context['user_achievements'] = user_achievements
        context['all_achievements'] = all_achievements
        context['unlocked_count'] = user_achievements.count()
        context['total_count'] = all_achievements.count()

        return context
