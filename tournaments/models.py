from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from decimal import Decimal


class PokerUser(AbstractUser):
    bankroll = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(0)],
    )

    @property
    def display_bankroll(self) -> str:
        return f"${self.bankroll:.2f}"

    def __str__(self) -> str:
        return f"{self.username} (${self.bankroll})"


class TournamentInput(models.Model):
    date = models.DateField()
    buy_in = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.10')), MaxValueValidator(10000)],
        null=False,
        blank=False,
    )
    cashed_for = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(4000000)],
        default=Decimal('0.00'),
        null=False,
        blank=False,
    )
    place_finished = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20000)],
        null=False,
        blank=False,
    )

    player = models.ForeignKey(
        'PokerUser',
        on_delete=models.CASCADE,
        related_name='tournaments'
    )

    @property
    def net_amount(self) -> Decimal:
        return Decimal(str(self.cashed_for)) - Decimal(str(self.buy_in))

    @property
    def is_itm(self) -> bool:
        return float(self.cashed_for) > 0.00

    @property
    def display_net(self) -> str:
        net = self.net_amount
        if net > 0:
            return f"+${net}"
        elif net < 0:
            return f"-${abs(net)}"
        return "$0.00"

    def __str__(self) -> str:
        return f"{self.date}: ${self.buy_in} ({self.display_net})"


class BankrollAdjustment(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('correction', 'Correction'),
    ]

    user = models.ForeignKey(
        'PokerUser',
        on_delete=models.CASCADE,
        related_name='adjustments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')),
                    MaxValueValidator(Decimal('4000000'))
                    ],
        null=False,
        blank=False,
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def apply_to_user(self):
        if self.transaction_type == 'deposit':
            self.user.bankroll += self.amount
        elif self.transaction_type == 'withdrawal':
            self.user.bankroll -= self.amount
        elif self.transaction_type == 'correction':
            self.user.bankroll = self.amount

        self.user.save()

    def __str__(self) -> str:
        return f"{self.user.username}: {self.transaction_type} ${self.amount}"


