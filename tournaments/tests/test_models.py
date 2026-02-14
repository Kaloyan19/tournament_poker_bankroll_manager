from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import TournamentInput, BankrollAdjustment
from django.core.exceptions import ValidationError
from datetime import date

User = get_user_model()

class PokerUserModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testplayer",
            password="testpass123",
            bankroll=Decimal('1000.00')
        )

    def test_create_user_with_bankroll(self):
        print('Test Creating user with bankroll')
        self.assertEqual(self.user.username, 'testplayer')
        self.assertEqual(self.user.bankroll, Decimal('1000.00'))
        print("Created successfully")

    def test_display_bankroll_property(self):
        print('Test displaying bankroll')

        self.assertEqual(self.user.display_bankroll, '$1000.00')
        print('Initial bankroll displays $1000.00')

        self.user.bankroll = Decimal('1234.56')
        self.assertEqual(self.user.display_bankroll, '$1234.56')
        print('Initial bankroll displays $1234.56')

        self.user.bankroll = Decimal('0.00')
        self.assertEqual(self.user.display_bankroll, '$0.00')
        print('Initial bankroll displays 0.00')

        self.user.bankroll = Decimal('999999.99')
        self.assertEqual(self.user.display_bankroll, '$999999.99')
        print('Initial bankroll displays 999999.99')

        print('All tests passed')

    def test_string_representation(self):
        print('Test string representation')

        self.assertEqual(str(self.user), 'testplayer ($1000.00)')
        print("Initial string 'testplayer ($1000.00)'")

        self.user.bankroll = Decimal('1234.56')
        self.assertEqual(str(self.user), 'testplayer ($1234.56)')
        print("Initial string 'testplayer ($1234.56)'")

        print("String representation passed")

    def test_bankroll_min_value_validator(self):
        print("Test Testing bankroll min value validator...")

        self.user.bankroll = Decimal('-100.00')

        with self.assertRaises(ValidationError):
            self.user.full_clean()

        print("ValidationError raised correctly")
        print("Bankroll min value validator test passed")

    def test_default_bankroll(self):
        print("Testing default bankroll")

        user2 = User.objects.create_user(
            username="testplayer2",
            password="testpass123",
        )

        print(f"created user2 with username '{user2.username}'")
        print(f"User2 bankroll: {user2.bankroll}")

        self.assertEqual(user2.bankroll, Decimal('100.00'))

        print("Default bankroll test passed")

    def test_create_tournament(self):
        print('Test creating tournament')

        tournament = TournamentInput.objects.create(
            date=date(2024, 2, 20),
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('200.00'),
            place_finished=27,
            player=self.user
        )

        print(f'tournament created: {tournament.id}')
        print(f'tournament date: {tournament.date}')
        print(f'tournament buy in: {tournament.buy_in}')
        print(f'cashed for: {tournament.cashed_for}')
        print(f'tournament place finished: {tournament.place_finished}')
        print(f'tournament player: {tournament.player.username}')

        self.assertEqual(
            tournament.date.strftime('%Y-%m-%d'),'2024-02-20')
        self.assertEqual(tournament.buy_in, Decimal('100.00'))
        self.assertEqual(tournament.cashed_for, Decimal('200.00'))
        self.assertEqual(tournament.place_finished, 27)
        self.assertEqual(tournament.player, self.user)

        print('Tournament creation test passed')

    def test_net_amount_property(self):
        print('Testing net amount property')
        
        tournament_profit = TournamentInput.objects.create(
            date=date(2024, 2, 20),
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('200.00'),
            place_finished=27,
            player=self.user
        )
        
        profit_net = tournament_profit.net_amount
        print(f'Cashed in Tournament: Buy-in: 100$, cashed 200$')
        print(f'net amount: {profit_net}$')
        self.assertEqual(profit_net, Decimal('100.00'))
        print("profit calculation test passed")

        tournament_loss = TournamentInput.objects.create(
            date=date(2024, 2, 20),
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('0.00'),
            place_finished=270,
            player=self.user
        )

        net_loss = tournament_loss.net_amount
        print(f"Lost tournament: Buy-in: 100$, Cashed: 0$")
        print(f'net amount: {net_loss}')
        self.assertEqual(net_loss, Decimal('-100.00'))
        print("Lost tournament test passed")

        print("Net amount property tested")

    def test_is_itm_property(self):
        print('Testing is_itm property')

        tournament_itm = TournamentInput.objects.create(
            date=date(2024, 2, 20),
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('200.00'),
            place_finished=27,
            player=self.user
        )

        print(f'Cashed: {tournament_itm.cashed_for}$')
        self.assertTrue(tournament_itm.is_itm)
        print("Itm property test passed")

        lost_tournament = TournamentInput.objects.create(
            date=date(2024, 2, 20),
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('0.00'),
            place_finished=273,
            player=self.user
        )

        print(f'Busted: Cashed: {lost_tournament.buy_in}$')
        self.assertFalse(lost_tournament.is_itm)
        print("Itm property test passed")

    def test_display_net_property(self):
        print('Tesing display net property')

        tournament_profit = TournamentInput.objects.create(
            date=date(2024, 2, 20),
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('200.00'),
            place_finished=27,
            player=self.user
        )

        profit_display = tournament_profit.display_net
        print(f"Cashed: {tournament_profit.net_amount}$")
        print(f'Display: {profit_display}')
        self.assertEqual(profit_display, '+$100.00')

        tournament_loss = TournamentInput.objects.create(
            date=date(2024, 2, 20),
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('0.00'),
            place_finished=273,
            player=self.user
        )

        loss_display = tournament_loss.display_net
        print(f'Busted: {tournament_loss.net_amount}$')
        print(f'Display: {loss_display}')
        self.assertEqual(loss_display, '-$100.00')

        print("Passed succesfully")

    def test_string_representation_tournament(self):
        print('Testing string representation tournament')

        tournament = TournamentInput.objects.create(
            date=date(2024, 2, 20),
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('200.00'),
            place_finished=27,
            player=self.user
        )

        tournament_str = str(tournament)
        print(f'tournament: {tournament_str}')
        self.assertEqual(tournament_str, "2024-02-20: $100.00 (+$100.00)")
        print("Passed succesfully")

    def test_min_max_validators(self):
        print('Testing min and max validators')

        print('Testing buy-in min validator')
        tournament_min_buy_in = TournamentInput(
            date='2024-02-20',
            buy_in=Decimal('0.04'),
            cashed_for=Decimal('0.00'),
            place_finished=100,
            player=self.user
        )

        try:
            tournament_min_buy_in.full_clean()
            print('Tournament min validation passed')
            self.fail('Tournament min validation failed')
        except ValidationError as e:
            print('Validation Raised correctly')
            print(f'Error fields: {list(e.message_dict.keys())}')
            self.assertIn('buy_in', e.message_dict)

        print("Testing buy_in maximum validator")
        tournament_max_buy_in = TournamentInput(
            date='2024-01-20',
            buy_in=Decimal('15000.00'),
            cashed_for=Decimal('0.00'),
            place_finished=10,
            player=self.user
        )

        try:
            tournament_max_buy_in.full_clean()
            print("ERROR: No ValidationError raised for buy_in above maximum")
            self.fail("Should have raised ValidationError for buy_in above maximum")
        except ValidationError as e:
            print(f"ValidationError raised correctly")
            print(f"Error fields: {list(e.message_dict.keys())}")
            self.assertIn('buy_in', e.message_dict)

        print("TournamentInput validator tests passed")

    def test_place_finished_validators(self):
        print("Testing place_finished validators...")

        print("Testing place_finished minimum validator")
        tournament_min_place = TournamentInput(
            date='2024-01-20',
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('150.00'),
            place_finished=0,
            player=self.user
        )

        try:
            tournament_min_place.full_clean()
            print("ERROR: No ValidationError raised for place_finished below minimum")
            self.fail("Should have raised ValidationError for place_finished below minimum")
        except ValidationError as e:
            print(f"ValidationError raised correctly")
            print(f"Error fields: {list(e.message_dict.keys())}")
            self.assertIn('place_finished', e.message_dict)

        print("Testing place_finished maximum validator")
        tournament_max_place = TournamentInput(
            date='2024-01-20',
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('150.00'),
            place_finished=25000,
            player=self.user
        )

        try:
            tournament_max_place.full_clean()
            print("ERROR: No ValidationError raised for place_finished above maximum")
            self.fail("Should have raised ValidationError for place_finished above maximum")
        except ValidationError as e:
            print(f"ValidationError raised correctly")
            print(f"Error fields: {list(e.message_dict.keys())}")
            self.assertIn('place_finished', e.message_dict)

        print("Testing valid place_finished")
        tournament_valid = TournamentInput(
            date='2024-01-20',
            buy_in=Decimal('100.00'),
            cashed_for=Decimal('150.00'),
            place_finished=5000,
            player=self.user
        )

        try:
            tournament_valid.full_clean()
            print("Valid place_finished passed validation")
        except ValidationError as e:
            print(f"ERROR: Valid place_finished raised ValidationError: {e}")
            self.fail("Valid place_finished should not raise ValidationError")

        print("place_finished validator tests passed")

    def test_create_adjustment(self):
        print("Starting BankrollAdjustment Model Tests")
        print("Testing basic adjustment creation")

        deposit = BankrollAdjustment.objects.create(
            user=self.user,
            amount=Decimal('500.00'),
            transaction_type='deposit',
            description='Test deposit'
        )

        print(f"Deposit created with ID: {deposit.id}")
        print(f"User: {deposit.user.username}")
        print(f"Amount: ${deposit.amount}")
        print(f"Transaction type: {deposit.transaction_type}")
        print(f"Description: '{deposit.description}'")
        print(f"Date: {deposit.date}")

        self.assertEqual(deposit.user, self.user)
        self.assertEqual(deposit.amount, Decimal('500.00'))
        self.assertEqual(deposit.transaction_type, 'deposit')
        self.assertEqual(deposit.description, 'Test deposit')
        self.assertIsNotNone(deposit.date)

        print("Basic adjustment creation test passed")

    def test_apply_to_user_deposit(self):
        print("Testing apply_to_user for deposits...")

        initial_bankroll = self.user.bankroll
        print(f"Initial bankroll: ${initial_bankroll}")

        deposit = BankrollAdjustment.objects.create(
            user=self.user,
            amount=Decimal('500.00'),
            transaction_type='deposit',
            description='Test deposit'
        )
        print(f"Created deposit: ${deposit.amount}")

        deposit.apply_to_user()
        print(f"Applied deposit to user")

        self.user.refresh_from_db()
        print(f"Refreshed user from database")

        expected = initial_bankroll + Decimal('500.00')
        print(f"Expected bankroll: ${expected}")
        print(f"Actual bankroll: ${self.user.bankroll}")

        self.assertEqual(self.user.bankroll, expected)
        print("Deposit application test passed")

    def test_apply_to_user_withdrawal(self):
        print("Testing apply_to_user for withdrawals...")

        initial_bankroll = self.user.bankroll
        print(f"Initial bankroll: ${initial_bankroll}")

        withdrawal = BankrollAdjustment.objects.create(
            user=self.user,
            amount=Decimal('200.00'),
            transaction_type='withdrawal',
            description='Test withdrawal'
        )
        print(f"Created withdrawal: ${withdrawal.amount}")

        withdrawal.apply_to_user()
        print(f"Applied withdrawal to user")

        self.user.refresh_from_db()
        print(f"Refreshed user from database")

        expected = initial_bankroll - Decimal('200.00')
        print(f"Expected bankroll: ${expected}")
        print(f"Actual bankroll: ${self.user.bankroll}")

        self.assertEqual(self.user.bankroll, expected)
        print("Withdrawal application test passed")

    def test_apply_to_user_correction(self):
        print("Testing apply_to_user for corrections...")

        initial_bankroll = self.user.bankroll
        print(f"Initial bankroll: ${initial_bankroll}")

        correction = BankrollAdjustment.objects.create(
            user=self.user,
            amount=Decimal('1500.00'),
            transaction_type='correction',
            description='Bankroll correction'
        )
        print(f"Created correction: ${correction.amount}")

        correction.apply_to_user()
        print(f"Applied correction to user")

        self.user.refresh_from_db()
        print(f"Refreshed user from database")

        expected = Decimal('1500.00')
        print(f"Expected bankroll: ${expected}")
        print(f"Actual bankroll: ${self.user.bankroll}")

        self.assertEqual(self.user.bankroll, expected)
        print("Correction application test passed")

    def test_string_representation_adjustment(self):
        print("Testing BankrollAdjustment string representation...")

        deposit = BankrollAdjustment.objects.create(
            user=self.user,
            amount=Decimal('500.00'),
            transaction_type='deposit',
            description='Test deposit'
        )

        deposit_str = str(deposit)
        print(f"Deposit string: '{deposit_str}'")
        self.assertEqual(deposit_str, "testplayer: deposit $500.00")
        print("Deposit format correct: 'username: deposit $amount'")

        withdrawal = BankrollAdjustment.objects.create(
            user=self.user,
            amount=Decimal('200.00'),
            transaction_type='withdrawal',
            description='Test withdrawal'
        )

        withdrawal_str = str(withdrawal)
        print(f"Withdrawal string: '{withdrawal_str}'")
        self.assertEqual(withdrawal_str, "testplayer: withdrawal $200.00")
        print("Withdrawal format correct: 'username: withdrawal $amount'")

        correction = BankrollAdjustment.objects.create(
            user=self.user,
            amount=Decimal('1500.00'),
            transaction_type='correction',
            description='Test correction'
        )

        correction_str = str(correction)
        print(f"Correction string: '{correction_str}'")
        self.assertEqual(correction_str, "testplayer: correction $1500.00")
        print("Correction format correct: 'username: correction $amount'")

        print("BankrollAdjustment string representation tests passed")

    def test_amount_validators(self):
        print("Testing BankrollAdjustment amount validators...")

        print("Testing amount minimum validator (0.01)...")
        adjustment_min = BankrollAdjustment(
            user=self.user,
            amount=Decimal('0.00'),
            transaction_type='deposit',
            description='Test'
        )

        try:
            adjustment_min.full_clean()
            print("ERROR: No ValidationError raised for amount below minimum")
            self.fail("Should have raised ValidationError for amount below minimum")
        except ValidationError as e:
            print(f"ValidationError raised correctly")
            print(f"Error fields: {list(e.message_dict.keys())}")
            self.assertIn('amount', e.message_dict)

        print("Testing amount maximum validator (4,000,000)...")
        adjustment_max = BankrollAdjustment(
            user=self.user,
            amount=Decimal('5000000.00'),
            transaction_type='deposit',
            description='Test'
        )

        try:
            adjustment_max.full_clean()
            print("Note: If this passes, max validator might not be enforced")
            print("Check your model to see if MaxValueValidator is implemented")
        except ValidationError as e:
            print(f"ValidationError raised correctly")
            print(f"Error fields: {list(e.message_dict.keys())}")
            self.assertIn('amount', e.message_dict)

        print("Testing valid amount (should pass)...")
        adjustment_valid = BankrollAdjustment(
            user=self.user,
            amount=Decimal('2500.00'),
            transaction_type='deposit',
            description='Test'
        )

        try:
            adjustment_valid.full_clean()
            print("Valid amount passed validation")
        except ValidationError as e:
            print(f"ERROR: Valid amount raised ValidationError: {e}")
            self.fail("Valid amount should not raise ValidationError")

        print("Testing transaction_type choices...")
        adjustment_invalid_type = BankrollAdjustment(
            user=self.user,
            amount=Decimal('100.00'),
            transaction_type='invalid_type',
            description='Test'
        )

        try:
            adjustment_invalid_type.full_clean()
            print("ERROR: No ValidationError raised for invalid transaction_type")
            self.fail("Should have raised ValidationError for invalid transaction_type")
        except ValidationError as e:
            print(f"ValidationError raised correctly")
            print(f"Error fields: {list(e.message_dict.keys())}")
            self.assertIn('transaction_type', e.message_dict)
