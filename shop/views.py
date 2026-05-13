class CommunityView(TemplateView):
    template_name = 'shop/community.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Последние отзывы
        recent_reviews = Review.objects.select_related('user', 'game').order_by('-created_at')[:12]

        # Последние покупки (анонимизированные)
        recent_purchases = OrderGame.objects.select_related('order__user', 'game').order_by('-order__created_at')[:10]

        context['recent_reviews'] = recent_reviews
        context['recent_purchases'] = recent_purchases
        return context
