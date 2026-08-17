from django.test import TestCase

from scuba.accounts.models import User
from scuba.diveshops.models import Diveshop


class TestDiveshopViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='diveshopuser@nowhere.com', username='diveshopuser', password='tester1234',
            first_name='Dive', last_name='Shopper')
        self.shop = Diveshop.objects.create(
            name='Local Shop', lat=33.767, long=-118.19, is_active=True)

    def test_index_requires_login(self):
        response = self.client.get('/diveshops/')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login'))

    def test_index_renders_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get('/diveshops/')

        self.assertEqual(response.status_code, 200)

    def test_getlocaldiveshops_requires_login(self):
        response = self.client.get('/diveshops/json/getlocaldiveshops/')

        self.assertEqual(response.status_code, 302)

    def test_getlocaldiveshops_returns_json_serializable_shops(self):
        self.client.force_login(self.user)

        response = self.client.get(
            '/diveshops/json/getlocaldiveshops/',
            {'lat': 34.0522, 'lon': -118.2437, 'radius': 50})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['name'], self.shop.name)
        self.assertEqual(data['items'][0]['id'], self.shop.pk_as_str)

    def test_getlocaldiveshops_without_params_returns_all_active(self):
        self.client.force_login(self.user)

        response = self.client.get('/diveshops/json/getlocaldiveshops/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['items']), 1)
