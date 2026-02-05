from datetime import datetime, timedelta
from django.db.models import Sum
from decimal import Decimal

def get_period_filter(period: str):
    today = datetime.now().date()

    if period == 'week':
        return today - timedelta(days=7), "Last 7 days"
    if period == 'month':
        return today - timedelta(days=30), "Last 30 Days"
    if period == 'year':
        return today - timedelta(days=365), "Last Year"

    return None, "All Time"

def calculate_tournament_stats(qs):
    total = qs.count()

    if total == 0:
        return {
            'total_tournaments': 0,
            'total_buy_ins': Decimal('0'),
            'total_cash': Decimal('0'),
            'total_profit': Decimal('0'),
            'roi': 0,
            'itm_count': 0,
            'itm_percentage': 0,
            'first_places': 0,
            'top_10_finishes': 0,
            'first_place_percentage': 0,
            'top_10_percentage': 0,
            'avg_buy_in': 0,
        }

    total_buy_ins = qs.aggregate(Sum('buy_in'))['buy_in__sum'] or Decimal('0')
    total_cash = qs.aggregate(Sum('cashed_for'))['cashed_for__sum'] or Decimal('0')
    total_profit = total_cash - total_buy_ins

    roi = (total_profit / total_buy_ins * 100) if total_buy_ins > 0 else 0

    itm_count = qs.filter(cashed_for__gt=0).count()
    itm_percentage = (itm_count / total * 100)

    first_places = qs.filter(place_finished=1).count()
    top_10_finishes = qs.filter(place_finished__lte=10).count()

    first_place_percentage = (first_places / total * 100)
    top_10_percentage = (top_10_finishes / total * 100)

    avg_buy_in = total_buy_ins / total

    return {
        'total_tournaments': total,
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
        'avg_buy_in': round(avg_buy_in, 2),
    }

def calculate_adjustment_totals(qs):
    total_deposits = qs.filter(
        transaction_type='deposit'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    total_withdrawals = qs.filter(
        transaction_type='withdrawal'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    return {
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
    }