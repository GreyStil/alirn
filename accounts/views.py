class FavoritesView(LoginRequiredMixin, View):
    template_name = 'accounts/profile_favorites.html'

    def get(self, request):
        games = request.user.profile.favorites.all()
        return render(request, self.template_name, {'games': games})
