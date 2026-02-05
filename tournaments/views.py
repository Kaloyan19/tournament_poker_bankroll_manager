from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TournamentInput, BankrollAdjustment
from .forms import TournamentInputForm, BankrollAdjustmentForm, PokerUserCreationForm
from django.contrib.auth import login
from .services import get_period_filter, calculate_tournament_stats, calculate_adjustment_totals


@login_required
def dashboard(request):
    period = request.GET.get('period', 'all')

    tournaments = TournamentInput.objects.filter(player=request.user)
    adjustments = BankrollAdjustment.objects.filter(user=request.user)

    start_date, period_display = get_period_filter(period)

    if start_date:
        tournaments = tournaments.filter(date__gte=start_date)
        adjustments = adjustments.filter(date__gte=start_date)

    tournaments = tournaments.order_by('-date')
    adjustments = adjustments.order_by('-date')

    stats = calculate_tournament_stats(tournaments)

    adjustment_totals = calculate_adjustment_totals(adjustments)

    context = {
        'tournaments': tournaments[:10],
        'adjustments': adjustments[:5],

        'current_period': period,
        'period_display': period_display,

        'user': request.user,
        'current_bankroll': request.user.bankroll,

        **stats,

        'total_deposits': adjustment_totals['total_deposits'],
        'total_withdrawals': adjustment_totals['total_withdrawals'],
    }

    return render(request, 'tournaments/dashboard.html', context)


@login_required
def add_tournament(request):
    if request.method == 'POST':
        form = TournamentInputForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.player = request.user
            tournament.save()

            request.user.bankroll += tournament.net_amount
            request.user.save()

            messages.success(request, f'Tournament added! Net: {tournament.display_net}')
            return redirect('tournaments:dashboard')

    else:
        form = TournamentInputForm()

    return render(request, 'tournaments/add_tournaments.html', {'form': form})


@login_required
def add_adjustment(request):
    if request.method == 'POST':
        form = BankrollAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.save(commit=False)
            adjustment.user = request.user
            adjustment.save()

            adjustment.apply_to_user()

            if adjustment.transaction_type == 'deposit':
                messages.info(request, f'Deposited {adjustment.amount}$')
            elif adjustment.transaction_type == 'withdrawal':
                messages.info(request, f'Withdrew {adjustment.amount}$')
            elif adjustment.transaction_type == 'correction':
                messages.info(request, f'Bankroll corrected to {adjustment.amount}$')

            return redirect('tournaments:dashboard')

    else:
        form = BankrollAdjustmentForm()

    return render(request, 'tournaments/add_adjustment.html', {'form': form})


@login_required
def tournament_list(request):
    period = request.GET.get('period', 'all')
    tournaments = TournamentInput.objects.filter(player=request.user)

    start_date, _ = get_period_filter(period)

    if start_date:
        tournaments = tournaments.filter(date__gte=start_date)

    total_count = tournaments.count()
    total_profit = sum(t.net_amount for t in tournaments)

    context = {
        'tournaments': tournaments.order_by('-date'),
        'total_count': total_count,
        'total_profit': total_profit,
        'current_period': period,
    }

    return render(request, 'tournaments/tournament_list.html', context)


@login_required
def edit_tournament(request, pk):
    tournament = get_object_or_404(TournamentInput, pk=pk, player=request.user)

    old_net_amount = tournament.net_amount

    if request.method == 'POST':
        form = TournamentInputForm(request.POST, instance=tournament)
        if form.is_valid():
            request.user.bankroll -= old_net_amount

            tournament = form.save()

            request.user.bankroll += tournament.net_amount
            request.user.save()

            messages.success(request, 'Tournament updated successfully!')
            return redirect('tournaments:tournament_list')
    else:
        form = TournamentInputForm(instance=tournament)

        return render(request, 'tournaments/edit_tournament.html', {'form': form, 'tournament': tournament})

@login_required
def delete_tournament(request, pk):
    tournament = get_object_or_404(TournamentInput, pk=pk, player=request.user)

    if request.method == 'POST':
        request.user.bankroll -= tournament.net_amount
        request.user.save()

        tournament.delete()

        messages.success(request, 'Tournament deleted successfully!')
        return redirect('tournaments:tournament_list')

    return render(request, 'tournaments/delete_tournament.html', {'tournament': tournament})


def signup(request):
    if request.method == 'POST':
        form = PokerUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('tournaments:dashboard')
    else:
        form = PokerUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})