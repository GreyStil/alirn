class OrderCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/order_complete.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            new_achievements = check_and_award_achievements(request.user)
            for ach in new_achievements:
                messages.success(
                    request, 
                    f'🏆 Получено достижение: <strong>{ach.name}</strong> (+{ach.points} очков)'
                )
        return super().get(request, *args, **kwargs)