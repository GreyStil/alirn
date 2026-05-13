class RemoveFromFavoritesView(LoginRequiredMixin, View):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        request.user.profile.favorites.remove(game)
        messages.success(request, f'"{game.title}" удалена из желаемого')
        return redirect('accounts:profile_favorites')
