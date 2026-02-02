from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime, timedelta
from decimal import Decimal
from .models import TournamentInput, BankrollAdjustment
from .forms import TournamentInputForm, BankrollAdjustmentForm


@login_required
def dashboard(request):
    period = request.GET.get('period', 'all')
    tournaments = TournamentInput.objects.filter(player=request.user)
    adjustments = BankrollAdjustment.objects.filter(user=request.user)
    today = datetime.now().date()
    period_display = "All Time"
    start_date = None

    if period == 'week':
        start_date = today - timedelta(days=7)
        tournaments = tournaments.filter(date__gte=start_date)
        period_display = "Last 7 days"
    elif period == 'month':
        start_date = today - timedelta(days=30)
        tournaments = tournaments.filter(date__gte=start_date)
        period_display = "Last 30 Days"
    elif period == 'year':
        start_date = today - timedelta(days=365)
        tournaments = tournaments.filter(date__gte=start_date)
        period_display = "Last Year"

    if start_date:
        adjustments = adjustments.filter(date__gte=start_date)

    tournaments = tournaments.order_by('-date')
    adjustments = adjustments.order_by('-date')

    total_tournaments = tournaments.count()

    if total_tournaments > 0:
        total_buy_ins = tournaments.aggregate(Sum('buy_in'))['buy_in__sum']
        total_cash = tournaments.aggregate(Sum('cashed_for'))['cashed_for__sum']
        total_profit = total_cash - total_buy_ins

        roi = (total_profit / total_buy_ins * 100)

        itm_count = tournaments.filter(cashed_for__gt=0).count()
        itm_percentage = (itm_count / total_tournaments * 100)

        first_places = tournaments.filter(place_finished=1).count()
        top_10_finishes = tournaments.filter(place_finished__lte=10).count()

        first_place_percentage = (first_places / total_tournaments * 100)
        top_10_percentage = (top_10_finishes / total_tournaments * 100)

        avg_buy_in = total_buy_ins  / total_tournaments

    else:
        total_buy_ins = Decimal('0')
        total_cash = Decimal('0')
        total_profit = Decimal('0')
        roi = 0
        itm_count = 0
        itm_percentage = 0
        first_places = 0
        top_10_finishes = 0
        first_place_percentage = 0
        top_10_percentage = 0
        avg_buy_in = Decimal('0')

    total_deposits = adjustments.filter(transaction_type='deposit').aggregate(Sum('amount'))['amount__sum']
    total_withdrawals = adjustments.filter(transaction_type='withdrawal').aggregate(Sum('amount'))['amount__sum']

    context = {
        'tournaments': tournaments[:10],
        'adjustments': adjustments[:5],
        'current_period': period,
        'period_display': period_display,

        'user': request.user,
        'current_bankroll': request.user.bankroll,

        'total_tournaments': total_tournaments,
        'total_buy_ins': total_buy_ins,
        'total_cash': total_cash,
        'total_profit': total_profit,

        'roi': round(roi, 2),
        'itm_count': itm_count,
        'itm_percentage': round(itm_percentage, 2),

        'first_places': first_places,
        'top_10_finishes': top_10_finishes,
        'first_place_percentage': round(first_place_percentage, 2),
        'top_10_percentage': round(top_10_percentage, 2),

        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,

        'avg_buy_in': round(avg_buy_in, 2),
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

            if adjustment.transaction_type == 'deposit':
                request.user.bankroll += adjustment.amount
                messages.info(request, f'Deposited {adjustment.amount}$')
            elif adjustment.transaction_type == 'withdrawal':
                request.user.bankroll -= adjustment.amount
                messages.info(request, f'Withdrew {adjustment.amount}$')
            elif adjustment.transaction_type == 'correction':
                request.user.bankroll = adjustment.amount
                messages.info(request, f'Bankroll corrected to {adjustment.amount}$')

            request.user.save()

            return redirect('tournaments:dashboard')

    else:
        form = BankrollAdjustmentForm()

    return render(request, 'tournaments/add_adjustment.html', {'form': form})


@login_required
def tournament_list(request):
    period = request.GET.get('period', 'all')
    tournaments = TournamentInput.objects.filter(player=request.user)

    if period != 'all':
        today = datetime.now().date()
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)

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