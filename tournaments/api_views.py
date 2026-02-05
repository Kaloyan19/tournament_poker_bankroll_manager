from decimal import Decimal
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import TournamentInput, BankrollAdjustment
from .serializers import TournamentSerializer, BankrollAdjustmentSerializer, UserSerializer
from datetime import datetime, timedelta
from .services import get_period_filter, calculate_tournament_stats, calculate_adjustment_totals

User = get_user_model()


class TournamentViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TournamentInput.objects.filter(player=self.request.user)

    def perform_create(self, serializer):
        serializer.save(player=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        tournaments = self.get_queryset()

        stats = calculate_tournament_stats(tournaments)

        stats_float = {
            key: float(value) if isinstance(value, (int, float, Decimal)) else value
            for key, value in stats.items()
        }

        return Response(stats_float)

class BankrollAdjustmentViewSet(viewsets.ModelViewSet):
    serializer_class = BankrollAdjustmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankrollAdjustment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        adjustment = serializer.save(user=self.request.user)
        adjustment.apply_to_user()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        totals = calculate_adjustment_totals(self.get_queryset())
        return Response({
            'total_deposits': float(totals['total_deposits']),
            'total_withdrawals': float(totals['total_withdrawals']),
        })


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        period = request.GET.get('period', 'all')
        user = request.user

        tournaments = TournamentInput.objects.filter(player=user)
        adjustments = BankrollAdjustment.objects.filter(user=user)

        start_date, period_display = get_period_filter(period)

        if start_date:
            tournaments = tournaments.filter(date__gte=start_date)
            adjustments = adjustments.filter(date__gte=start_date)

        tournaments = tournaments.order_by('-date')
        adjustments = adjustments.order_by('-date')

        stats = calculate_tournament_stats(tournaments)

        adjustment_totals = calculate_adjustment_totals(adjustments)

        recent_tournaments = tournaments[:10]
        recent_adjustments = adjustments[:5]

        tournament_serializer = TournamentSerializer(recent_tournaments, many=True)
        adjustment_serializer = BankrollAdjustmentSerializer(recent_adjustments, many=True)

        stats_float = {
            key: float(value) if isinstance(value, (int, float, Decimal)) else value
            for key, value in stats.items()
        }

        return Response({
            'period': period,
            'period_display': period_display,
            'user': {
                'id': user.id,
                'username': user.username,
                'bankroll': float(user.bankroll),
            },
            'stats': {
                **stats_float,
                'total_deposits': float(adjustment_totals['total_deposits']),
                'total_withdrawals': float(adjustment_totals['total_withdrawals']),
                'net_adjustments': float(
                    adjustment_totals['total_deposits'] - adjustment_totals['total_withdrawals']
                ),
            },
            'recent_tournaments': tournament_serializer.data,
            'recent_adjustments': adjustment_serializer.data,
        })

    # for charts in the future:)
    @action(detail=False, methods=['get'])
    def bankroll_history(self, request):

        days = int(request.GET.get('days', 30))
        user = request.user

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        tournaments = TournamentInput.objects.filter(
            player=user,
            date__range=[start_date.date(), end_date.date()]
        ).order_by('date')

        adjustments = BankrollAdjustment.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('date')

        bankroll_history = []
        running_total = float(user.bankroll)

        return Response({
            'labels': [f'Day {i}' for i in range(days)],
            'data': [float(user.bankroll) * (1 + i / days) for i in range(days)],
            'message': 'Bankroll history endpoint - implement detailed calculation as needed'
        })


