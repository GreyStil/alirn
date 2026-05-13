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

            # Достижения этой игры
            game_achievements = game.achievements.all()
            user_achievements = self.request.user.achievements.filter(
                achievement__in=game_achievements
            ).values_list('achievement_id', flat=True)

            context['game_achievements'] = game_achievements
            context['user_achievements_ids'] = list(user_achievements)
            context['unlocked_count'] = len(user_achievements)
            context['total_achievements'] = game_achievements.count()

        return context
