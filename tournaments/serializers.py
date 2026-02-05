from rest_framework import serializers
from decimal import Decimal
from .models import TournamentInput, BankrollAdjustment, PokerUser

class TournamentSerializer(serializers.ModelSerializer):
    net_amount = serializers.ReadOnlyField()
    display_net = serializers.ReadOnlyField()
    is_itm = serializers.ReadOnlyField()

    class Meta:
        model = TournamentInput
        fields = [
            'id',
            'date',
            'buy_in',
            'cashed_for',
            'place_finished',
            'player',
            'net_amount',
            'display_net',
            'is_itm',
        ]
        read_only_fields = ['player']

    def validate_buy_in(self, value):
        if value < Decimal('0.10'):
            raise serializers.ValidationError("Minimum buy-in is $0.10")
        if value > Decimal('10000'):
            raise serializers.ValidationError("Maximum buy-in is $10,000")
        return value

    def validate_cashed_for(self, value):
        if value < 0:
            raise serializers.ValidationError("Cash amount cannot be negative")
        if value > Decimal('4000000'):
            raise serializers.ValidationError("Maximum cash amount is $4,000,000")
        return value

    def validate_place_finished(self, value):
        if value < 1:
            raise serializers.ValidationError("Finish position must be at least 1")
        if value > 20000:
            raise serializers.ValidationError("Finish position seems unusually high")
        return value

    def validate_date(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Tournament date cannot be in the future")
        return value

class BankrollAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankrollAdjustment
        fields = [
            'id',
            'amount',
            'transaction_type',
            'description',
            'date',
            'user'
        ]
        read_only_fields = ['user', 'date']

    def validate_amount(self, value):
        if value < Decimal('0.01'):
            raise serializers.ValidationError("Minimum transaction amount is $0.01")
        if value > Decimal('4000000'):
            raise serializers.ValidationError("Maximum single transaction is $4,000,000")
        return value

    def validate_transaction_type(self, value):
        valid_types = ['deposit', 'withdrawal', 'correction']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"
            )
        return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokerUser
        fields = [
            'id',
            'username',
            'bankroll'
        ]
        read_only_fields = ['bankroll']

    def validate_bankroll(self, value):
        if value < 0:
            raise serializers.ValidationError("Bankroll cannot be negative")
        return value