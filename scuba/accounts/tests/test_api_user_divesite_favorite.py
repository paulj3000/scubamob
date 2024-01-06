"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.divesites.models import Divesite


class TestUserDivesiteFavoriteAPI(TestCase):
    fixtures = ["test_divesites.json", "test_users.json", "test_sitesettings.json"]

    def test_unauthenticated_set_divesite_favorite(self):
        """
        Test try to set a favorite password
        """
        client = APIClient()
        divesite = Divesite.objects.all().first()

        payload = {
            'divesite_id': divesite.pk_as_str
        }

        client = APIClient()
        response = client.post('/api/user/divesites/favorites/', payload, format='json')

        # nope, the user needs to be logged in
        self.assertEqual(response.status_code, 401)

    def test_add_favorite_divesite(self):
        """
        Test setting of a favorite divesite
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.all().first()

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'divesite_id': divesite.pk_as_str
        }

        response = client.post('/api/user/divesites/favorites/', payload, format='json')
        self.assertEqual(response.status_code, 201)

        new = response.json()
        self.assertEqual(len(new['id']), 32)
        self.assertIn('divesite', new)
        self.assertIn('name', new['divesite'])
        self.assertIn('description', new['divesite'])
        self.assertIn('lat', new['divesite'])

    def test_listing_favorite_divesites(self):
        """
        Test the listing of favorite divesites
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.all().first()

        # add the divesite into the database
        user.set_divesite_favorite(divesite)

        # and query for the divesites
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/user/divesites/favorites/', format='json')
        self.assertEqual(response.status_code, 200)
        the_list = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('favorites', the_list)
        self.assertEqual(len(the_list['favorites']), 1)
        self.assertIn('id', the_list['favorites'][0])
        self.assertIn('divesite', the_list['favorites'][0])

    def test_retrieve_favorite_divesites(self):
        """
        Test when a user retrieves a favorite divesite
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.all().first()

        # add the divesite into the database
        obj = user.set_divesite_favorite(divesite)

        # and query for the divesites
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f'/api/user/divesites/favorites/{obj.pk_as_str}/', format='json')
        self.assertEqual(response.status_code, 200)
        the_list = response.json()
        self.assertIn('id', the_list)
        self.assertIn('divesite', the_list)

    def test_delete_favorite_divesite(self):
        """
        Test when a user deletes a favorite
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.all().first()

        # add the divesite into the database
        obj = user.set_divesite_favorite(divesite)

        # and query for the divesites
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.delete(f'/api/user/divesites/favorites/{obj.pk_as_str}/')
        self.assertEqual(response.status_code, 204)

        response = client.get(f'/api/user/divesites/favorite/{obj.pk_as_str}/', format='json')
