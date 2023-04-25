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
    def test_buddies_search(self):
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/search?q=Test', format='json')
        self.assertEqual(response.status_code, 200)

        results = response.json()
        self.assertIsNotNone(results.get('search'), 'results contains search element')
        self.assertIsNotNone(results['search'].get('buddies'), 'Search key contains a buddies list')
        self.assertEqual(len(results['search']['buddies']), 4, 'Returning four buddies')

        # test case insensitivity
        response = client.get('/api/search?q=TEST', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results['search']['buddies']), 4, 'Returning four buddies')

