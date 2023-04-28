"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User


class TestSearchAPI(TestCase):
    fixtures = ["test_divesites.json", "test_users.json", "test_sitesettings.json"]
    def test_users_search(self):
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/search?q=Test', format='json')
        self.assertEqual(response.status_code, 200)

        results = response.json()
        self.assertIsNotNone(results.get('users'), 'Search key contains a users list')
        self.assertEqual(len(results['users']), 4, 'Returning four users')

        # test case insensitivity
        response = client.get('/api/search?q=TEST', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results['users']), 4, 'Returning four users')

    def test_self_user_search(self):
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/search?q=First', format='json')
        self.assertEqual(response.status_code, 200)
        results = response.json()

        # make sure
        self.assertEqual(
            len(results['users']), 2,
            'The user himself should not be returned')

        for search_user in results.get('users'):
            self.assertNotEqual(
                user.id,
                search_user['id'],
                f"{search_user['id']} doesn't match")

    def test_self_not_user_search(self):
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/search?q=First&c=c', format='json')
        self.assertEqual(response.status_code, 200)
        results = response.json()

        self.assertIsNone(results.get('users'))

    def test_self_not_user_logged_in_search(self):
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()

        response = client.get('/api/search?q=First&c=b', format='json')
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertIsNone(results.get('users'))

        response = client.get('/api/search?q=First', format='json')
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertIsNone(results.get('users'))
