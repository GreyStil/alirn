from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Game, Review, Ticket, TicketReply

class IndexView(TemplateView):
    template_name = 'shop/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_games'] = Game.objects.filter(discount_percent__gt=0)[:5]
        context['popular_games'] = Game.objects.order_by('-sales_count')[:6]
        return context

class CatalogView(View):
    template_name = 'shop/catalog.html'
    def get(self, request):
        games = Game.objects.all()
        genre = request.GET.get('genre', '')
        if genre:
            games = games.filter(genre=genre)
        paginator = Paginator(games, 12)
        return render(request, self.template_name, {'games': paginator.get_page(request.GET.get('page', 1)), 'genres': [('action','Action'),('rpg','RPG'),('indie','Indie')]})

class GameDetailView(DetailView):
    model = Game
    template_name = 'shop/game_detail.html'
    context_object_name = 'game'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        if self.request.user.is_authenticated:
            context['user_review'] = self.object.reviews.filter(user=self.request.user).first()
            context['is_owned'] = self.request.user.profile.owned_games.filter(id=self.object.id).exists()
        return context

class CartView(View):
    template_name = 'shop/cart.html'
    def get(self, request):
        games = request.user.cart.games.all() if request.user.is_authenticated else []
        return render(request, self.template_name, {'games': games})

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        if request.user.profile.owned_games.filter(id=game_id).exists():
            messages.warning(request, 'У вас уже есть эта игра')
            return redirect('shop:game_detail', pk=game_id)
        request.user.cart.games.add(game)
        messages.success(request, f'{game.title} добавлена в корзину')
        return redirect('shop:cart')

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, game_id):
        request.user.cart.games.remove(get_object_or_404(Game, id=game_id))
        messages.success(request, 'Игра удалена из корзины')
        return redirect('shop:cart')

class CheckoutView(LoginRequiredMixin, View):
    template_name = 'shop/checkout.html'
    def get(self, request):
        games = request.user.cart.games.all()
        total = sum(g.current_price for g in games)
        return render(request, self.template_name, {'games': games, 'total': total})

class OrderCompleteView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/order_complete.html'

# ==================== MODERATOR ====================
class ModeratorReviewsView(UserPassesTestMixin, ListView):
    model = Review
    template_name = 'shop/moderator_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 25

    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user.profile, 'is_moderator', False)

    def get_queryset(self):
        return Review.objects.select_related('user', 'game').order_by('-created_at')

class DeleteReviewModeratorView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and getattr(self.request.user.profile, 'is_moderator', False)

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        messages.success(request, 'Отзыв удалён')
        return redirect('shop:moderator_reviews')

# ==================== TICKETS ====================
class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'shop/ticket_list.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        if self.request.user.profile.is_support:
            return Ticket.objects.all().select_related('user').order_by('-created_at')
        return Ticket.objects.filter(user=self.request.user).order_by('-created_at')

class CreateTicketView(LoginRequiredMixin, View):
    template_name = 'shop/create_ticket.html'
    def get(self, request):
        return render(request, self.template_name)
    def post(self, request):
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if subject and message:
            Ticket.objects.create(user=request.user, subject=subject, message=message)
            messages.success(request, 'Заявка успешно создана!')
            return redirect('shop:ticket_list')
        messages.error(request, 'Заполните тему и описание')
        return render(request, self.template_name)

class TicketDetailView(LoginRequiredMixin, View):
    template_name = 'shop/ticket_detail.html'

    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.user != request.user and not request.user.profile.is_support:
            messages.error(request, 'Нет доступа')
            return redirect('shop:ticket_list')
        return render(request, self.template_name, {
            'ticket': ticket,
            'replies': ticket.replies.select_related('user').all()
        })

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.user != request.user and not request.user.profile.is_support:
            return redirect('shop:ticket_list')

        message = request.POST.get('message', '').strip()
        if message:
            TicketReply.objects.create(
                ticket=ticket,
                user=request.user,
                message=message,
                is_staff_reply=request.user.profile.is_support
            )
            if request.user.profile.is_support and ticket.status == 'open':
                ticket.status = 'in_progress'
                ticket.save()
        return redirect('shop:ticket_detail', pk=pk)
