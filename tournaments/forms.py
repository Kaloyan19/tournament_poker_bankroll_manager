from django import forms
from .models import TournamentInput, BankrollAdjustment
from decimal import Decimal

class TournamentInputForm(forms.ModelForm):
    class Meta:
        model = TournamentInput
        fields = ['date', 'buy_in', 'cashed_for', 'place_finished']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'buy_in': forms.NumberInput(attrs={'step': '0.01', 'min': '0.10', 'class': 'form-control'}),
            'cashed_for': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'place_finished': forms.NumberInput(attrs={'min': '1', 'class': 'form-control'}),
        }

    def clean_buy_in(self):
        buy_in = self.cleaned_data.get('buy_in')

        if buy_in is None:
            raise forms.ValidationError("Buy-in amount is required")

        if buy_in < Decimal('0.10'):
            raise forms.ValidationError("Minimum buy-in is 0.10$")

        if buy_in > Decimal('10000'):
            raise forms.ValidationError("Maximum buy-in is 10,000$")

        return buy_in

    def clean_cashed_for(self):
        cashed_for = self.cleaned_data.get('cashed_for')

        if cashed_for is None:
            return Decimal('0.00')

        if cashed_for < Decimal('0'):
            raise forms.ValidationError("Cash amount cannot be negative")

        if cashed_for > Decimal('4000000'):
            raise forms.ValidationError("Maximum cash amount is 4,000,000$")

        return cashed_for

    def clean_place_finished(self):
        place = self.cleaned_data.get('place_finished')

        if place is None:
            raise forms.ValidationError("Finish position is required")

        if place < 1:
            raise forms.ValidationError("Finish position must be at least 1")

        if place > 20000:
            raise forms.ValidationError("Finish position seems unusually high")

        return place

    def clean_date(self):
        date = self.cleaned_data.get('date')

        if date is None:
            raise forms.ValidationError("Date is required")

        from datetime import date as datetime_date
        if date > datetime_date.today():
            raise forms.ValidationError("Tournament date cannot be in the future")

        return date

    def clean(self):
        cleaned_data = super().clean()

        buy_in = cleaned_data.get('buy_in')
        cashed_for = cleaned_data.get('cashed_for')
        place = cleaned_data.get('place_finished')

        return cleaned_data

class BankrollAdjustmentForm(forms.ModelForm):
    class Meta:
        model = BankrollAdjustment
        fields = ['amount', 'transaction_type', 'description']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PayPal deposit'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if amount is None:
            raise forms.ValidationError("Amount is required")

        if amount <= Decimal('0'):
            raise forms.ValidationError("Amount must be greater than 0")

        if amount > Decimal('400000'):
            raise forms.ValidationError("Maximum single transaction is 4,000,000$")

        return amount

    def clean_transaction_type(self):
        transaction_type = self.cleaned_data.get('transaction_type')

        if transaction_type is None:
            raise forms.ValidationError("Transaction type is required")

        valid_types = ['deposit', 'withdrawal', 'correction']
        if transaction_type not in valid_types:
            raise forms.ValidationError("Invalid transaction type")

        return transaction_type

    def clean(self):
        cleaned_data = super().clean()

        amount = cleaned_data.get('amount')
        transaction_type = cleaned_data.get('transaction_type')

        return cleaned_data