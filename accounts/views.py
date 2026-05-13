class BalanceTopupView(LoginRequiredMixin, View):
    template_name = 'accounts/balance_topup.html'

    def get(self, request):
        return render(request, self.template_name, {'quick_amounts': [500, 1000, 1500, 2000, 5000]})

    def post(self, request):
        try:
            amount = Decimal(request.POST.get('amount'))
            if amount > 0:
                # Создаём запись о пополнении
                BalanceTopUp.objects.create(user=request.user, amount=amount)

                # Автоматически зачисляем на баланс
                profile = request.user.profile
                profile.balance += amount
                profile.save()

                # Проверяем и выдаём достижения (включая "Инвестор")
                new_achievements = check_and_award_achievements(request.user)

                messages.success(request, f'Баланс успешно пополнен на {amount} ₽')

                for ach in new_achievements:
                    messages.success(request, f'🏆 Получено достижение: {ach.name} (+{ach.points} очков)')

                return redirect('accounts:profile_balance')
            else:
                messages.error(request, 'Сумма должна быть больше нуля')
        except:
            messages.error(request, 'Неверная сумма')

        return render(request, self.template_name, {'quick_amounts': [500, 1000, 1500, 2000, 5000]})
