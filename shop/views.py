from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Game, Review, Ticket, TicketReply
from shop.utils.achievements import check_and_award_achievements


class OrderCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/order_complete.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            new_achievements = check_and_award_achievements(request.user)
            for ach in new_achievements:
                messages.success(request, f'Получено достижение: {ach.name} (+{ach.points} очков)')
        return super().get(request, *args, **kwargs)


class GameDetailView(DetailView):
    model = Game
    template_name = 'shop/game_detail.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.object
        context['reviews'] = game.reviews.all()

        if self.request.user.is_authenticated:
            context['user_review'] = game.reviews.filter(user=self.request.user).first()
            context['is_owned'] = self.request.user.profile.owned_games.filter(id=game.id).exists()

            game_achievements = game.achievements.all()
            user_achievements = self.request.user.achievements.filter(achievement__in=game_achievements).values_list('achievement_id', flat=True)

            context['game_achievements'] = game_achievements
            context['user_achievements_ids'] = list(user_achievements)
            context['unlocked_count'] = len(user_achievements)
            context['total_achievements'] = game_achievements.count()

        return context
