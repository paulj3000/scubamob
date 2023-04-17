"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.divesites.models import Divesite


class TestUserDivesitesApi(TestCase):
    fixtures = ["test_divesites.json", "test_users.json"]

    def test_add_divesite_review(self):
        """
        Write a review
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.get(name='White Point')

        payload = {
            'review': 'Today is a good day',
            'rating': 4,
            'review_date': date.today(),
        }

        client = APIClient()
        client.force_authenticate(user=user)

        url = f'/api/divesites/{divesite.pk_as_str}/reviews/'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)

        # now attempt to add another review for today, this one should fail
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_favorite_divesite(self):
        """
        Verify if a divesite is a favorite
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.get(name='White Point')

        client = APIClient()
        client.force_authenticate(user=user)

        url = f'/api/divesites/{divesite.pk_as_str}/favorite/'
        response = client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 202)

        favorite = user.favorites.get(divesite=divesite)
        self.assertTrue(favorite.is_favorite)

        payload = {
            'favorite': False
        }

        url = f'/api/divesites/{divesite.pk_as_str}/favorite/'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 202)

        favorite = user.favorites.get(divesite=divesite)
        self.assertFalse(favorite.is_favorite)

        payload = {
            'favorite': True
        }

        url = f'/api/divesites/{divesite.pk_as_str}/favorite/'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 202)

        favorite = user.favorites.get(divesite=divesite)
        self.assertTrue(favorite.is_favorite)

    def test_get_divesite_favorites(self):
        """
        Get all of my favorites
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.get(name='White Point')
        divesite.add_to_favorite(user)

        client = APIClient()
        client.force_authenticate(user=user)

        url = f'/api/divesites/favorites'
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        favorites = response.json().get('favorites')
        self.assertEqual(len(favorites), 1)

    def test_get_divesite(self):
        """
        Get a divesite
        """
        divesite = Divesite.objects.get(name='White Point')

        client = APIClient()

        url = f'/api/divesites/{divesite.pk_as_str}'
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        divesite = response.json().get('divesite')
        self.assertIsNotNone(divesite)
        self.assertEqual(divesite['id'], divesite['id'])
        self.assertEqual(divesite['name'], divesite['name'])
        self.assertEqual(divesite['description'], divesite['description'])
        self.assertEqual(divesite['banner'], divesite['banner'])
