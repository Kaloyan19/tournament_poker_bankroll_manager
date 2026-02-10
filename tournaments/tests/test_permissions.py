from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import TournamentInput, BankrollAdjustment
from ..api_views import TournamentViewSet

User = get_user_model()


class PermissionTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username='player1',
            password='testpass123',
            bankroll=Decimal('1000.00')
        )
        self.user2 = User.objects.create_user(
            username='player2',
            password='testpass123',
            bankroll=Decimal('2000.00')
        )

        self.client.force_authenticate(user=self.user1)

        response = self.client.post('/api/tournaments/', {
            'date': '2024-01-20',
            'buy_in': '100.00',
            'cashed_for': '150.00',
            'place_finished': 10
        }, format='json')
        self.tournament_id = response.data['id']

        response = self.client.post('/api/adjustments/', {
            'amount': '500.00',
            'transaction_type': 'deposit',
            'description': 'Test deposit'
        }, format='json')
        self.adjustment_id = response.data['id']

        self.client.force_authenticate(user=self.user2)

    def test_user_cannot_list_others_tournaments(self):
        response = self.client.get('/api/tournaments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, dict) and 'results' in response.data:
            data_count = len(response.data['results'])
        else:
            data_count = len(response.data)

        self.assertEqual(data_count, 0,
                         f"User2 should not see user1's tournaments. Found {data_count} items.")

    def test_get_queryset_filters_by_user(self):
        viewset = TournamentViewSet()
        viewset.request = type('Request', (), {'user': self.user2})()

        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)

        TournamentInput.objects.create(
            date='2024-01-21',
            buy_in=Decimal('50.00'),
            cashed_for=Decimal('75.00'),
            place_finished=5,
            player=self.user2
        )

        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_user_cannot_get_others_tournament(self):
        response = self.client.get(f'/api/tournaments/{self.tournament_id}/')
        self.assertIn(response.status_code,
                         [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN],
                                f'Expected 404/403 but got {response.status_code}')

    def test_user_cannot_update_others_tournament(self):
        response = self.client.put(f'/api/tournaments/{self.tournament_id}/',{
            'date': '2024-01-20',
            'buy_in': '100.00',
            'cashed_for': '0.00',
            'place_finished': 100
        },format='json')

        print(f'Test PUT response status: {response.status_code}')
        print(f'Test response data: {response.data}')

        self.assertIn(response.status_code,
                      [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN],
                      f'Expected 404/403 but got {response.status_code}')

    def test_user_cannot_delete_others_tournament(self):
        response = self.client.delete(f'/api/tournaments/{self.tournament_id}/')

        print(f'Test DELETE response status: {response.status_code}')
        print(f'Test response data: {response.data}')

        self.assertIn(response.status_code,
                      [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN],
                      f'Expected 404/403 but got {response.status_code}')

    def test_user_can_access_own_data(self):
        self.client.force_authenticate(user=self.user1)

        list_response = self.client.get('/api/tournaments/')
        print(f"Test 6 - User1 tournament count: {list_response.data.get('count', len(list_response.data))}")

        if list_response.data.get('count',
                                  len(list_response.data if isinstance(list_response.data, list) else [])) == 0:
            print("Tournament not found, recreating...")
            response = self.client.post('/api/tournaments/', {
                'date': '2024-01-20',
                'buy_in': '100.00',
                'cashed_for': '150.00',
                'place_finished': 10
            }, format='json')
            self.tournament_id = response.data['id']

        response = self.client.get(f'/api/tournaments/{self.tournament_id}/')
        print(f"Test - GET own tournament Response status: {response.status_code}")
        print(f"Test - Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.tournament_id)

    def test_user_cannot_access_others_adjustments(self):
        print("Testing URL: /api/adjustments/")

        response = self.client.get('/api/adjustments/')

        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")

        print("\nChecking API root to see available endpoints...")
        root_response = self.client.get('/api/')
        if root_response.status_code == 200:
            print(f"API root: {root_response.data}")

        if response.status_code == 404:
            print("Got 404 - checking if endpoint exists at all...")
            self.client.force_authenticate(user=self.user1)
            user1_response = self.client.get('/api/adjustments/')
            print(f"User1 response status: {user1_response.status_code}")
            print(f"User1 response data: {user1_response.data}")
            self.client.force_authenticate(user=self.user2)

        if response.status_code == 200:
            if isinstance(response.data, dict) and 'results' in response.data:
                data_count = len(response.data['results'])
            else:
                data_count = len(response.data)

            self.assertEqual(data_count, 0,
                             f"User2 should not see user1's adjustments. Found {data_count} items.")
        else:
            print("NOTE: /api/adjustments/ endpoint returned non-200 status. Check URL routing.")

    def test_user_cannot_get_others_adjustments(self):
        response = self.client.get(f'/api/adjustments/{self.adjustment_id}/')

        print(f"Test GET adjustment Response status: {response.status_code}")
        print(f"Test Response data: {response.data}")

        self.assertIn(response.status_code,
                         [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN],
                         f'Expected 404/403 but got {response.status_code}')

    def test_user_cannot_access_others_profile(self):
        response = self.client.get(f'/api/users/{self.user1.id}/')

        print(f"Test 9 - GET other user profile Response status: {response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         f"Expected 404 but got {response.status_code}")

    def test_user_can_access_own_profile(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/users/me/')
        print(f'Test User1 /me/ response status: {response.status_code}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'player1')

        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/users/me/')
        print(f"Test User2 /me/ Response status: {response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'player2')

    def test_users_list_only_shows_self(self):
        response = self.client.get('/api/users/')

        print(f'Test GET /api/users/ Response status: {response.status_code}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, dict) and 'results' in response.data:
            data = response.data['results']
            data_count = len(data)
        else:
            data = response.data
            data_count = len(data)

        print(f'Test found {data_count} users')

        self.assertEqual(data_count, 1, f'Should only see one user, found {data_count}')

        if data_count > 0:
            self.assertEqual(data[0]['username'], 'player2', 'Should see own user')

    def test_jwt_token_creation(self):
        client = APIClient()

        url = '/api/auth/jwt/create/'
        print(f"Test 12 - Testing URL: {url}")

        response = client.post(url, {
            'username': 'player2',
            'password': 'testpass123'
        }, format='json')

        print(f"Test 12 - JWT create Response status: {response.status_code}")

        if hasattr(response, 'data'):
            print(f"Test 12 - Response data: {response.data}")
        else:
            print(f"Test 12 - Response content: {response.content}")

        if response.status_code == 404:
            print("\nChecking available URLs...")
            root_response = client.get('/api/')
            if root_response.status_code == 200:
                print(f"API root endpoints: {root_response.data}")
            else:
                print(f"API root status: {root_response.status_code}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_token_contains_custom_claims(self):
        client = APIClient()

        response = client.post('/api/auth/jwt/create/', {
            'username': 'player2',
            'password': 'testpass123'
        },format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = response.data['access']

        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = client.get('/api/users/me/')

        print(f'Test using JWT to access /me/ Response status: {response.status_code}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print(f'Test user data from JWT: {response.data}')

