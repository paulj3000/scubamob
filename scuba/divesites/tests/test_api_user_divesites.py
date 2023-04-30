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
from scuba.divesites.models import Divesite, DivesiteCheckin, DivesiteCheckinThank


class TestUserDivesitesApi(TestCase):
    fixtures = ["test_divesites.json", "test_users.json", "test_sitesettings.json"]

    def test_add_divesite_review(self):
        """
        Write a review
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test4@tester.com')
        divesite = Divesite.objects.get(name='White Point')

        payload = {
            'review': 'Today is a good day',
            'rating': 4,
            'temp_c': 30.5,
            'visibility': 200,
            'review_date': date.today(),
        }

        client = APIClient()
        client.force_authenticate(user=user)

        url = f'/api/divesites/{divesite.pk_as_str}/reviews/'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)

        review = response.json()
        self.assertIsNotNone(review)
        self.assertEqual(review['id'], review['id'])

        # now attempt to add another review for today, this one should fail
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400)

        # now, make sure another user can add a review for the same
        # divesite (they shouldn't clash)
        client = APIClient()
        client.force_authenticate(user=user2)

        url = f'/api/divesites/{divesite.pk_as_str}/reviews/'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)

    def test_invalid_divesite_review(self):
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.get(name='White Point')

        url = f'/api/divesites/{divesite.pk_as_str}/reviews/'
        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'review': 'Today is a good day',
            'rating': 4,
            'temp_c': 300.5,
            'visibility': 200,
            'review_date': date.today(),
        }

        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400, "temperature too high")

        payload.update({'temp_c': 32, 'visibility': 5000})
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400, "visibility too high")

        payload.update({'temp_c': -32, 'visibility': 50})
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400, "temperature too low")

        payload.update({'temp_c': 32, 'rating': 0})
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400, "rating too low")

        payload.update({'temp_c': 32, 'rating': 6})
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400, "rating too high")

    def test_checkin_divesite(self):
        """
        Check into a divesite
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.get(name='White Point')

        client = APIClient()
        client.force_authenticate(user=user)

        url = f'/api/divesites/{divesite.pk_as_str}'
        response = client.get(url, format='json')
        divesiteData = response.json().get('divesite')
        self.assertIsNotNone(divesiteData)
        self.assertEqual(divesiteData['checkins'], 0, 'no checkins yet')

        # get the checkin url
        url = f'/api/divesites/{divesite.pk_as_str}/checkin/'
        client.force_authenticate(user=user)

        note = 'This was a good day'
        payload = {
            'note': note,
            'temp_c': 23,
            'visibility': 300,
        }
        response = client.post(url, {'note': note}, format='json')
        self.assertEqual(response.status_code, 201)

        checkin = response.json()
        self.assertIsNotNone(checkin['id'])
        self.assertIsNotNone(checkin['checkin_date'])

        # try again, make sure we cannot add another checkin for today
        response = client.post(url, {'note': note}, format='json')
        self.assertEqual(response.status_code, 400)

        url = f'/api/divesites/{divesite.pk_as_str}'
        response = client.get(url, format='json')
        divesite = response.json().get('divesite')
        self.assertIsNotNone(divesite)
        self.assertEqual(divesite['checkins'], 1, 'we now have a checkin')

    def test_invalid_checkin(self):
        payload = {
            'note': 'Today is a good day',
            'temp_c': 300.5,
            'visibility': 200,
            'review_date': date.today(),
        }

        # get the checkin url, divesite and user
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.get(name='White Point')
        url = f'/api/divesites/{divesite.pk_as_str}/checkin/'

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400, "temperature too high")

        payload = {
            'note': 'Today is a good day',
            'temp_c': 300.5,
            'visibility': 200,
            'review_date': date.today(),
        }

        payload.update({'temp_c': -32, 'visibility': 50})
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 400, "temperature too low")

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

    def test_thank_checkin_divesite(self):
        """
        Verify if a divesite is a favorite
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test2@tester.com')
        divesite = Divesite.objects.get(name='White Point')

        checkin = divesite.checkins.create(user=user)

        client = APIClient()
        client.force_authenticate(user=user2)

        url = f'/api/divesites/checkins/{checkin.pk_as_str}/thank/'
        response = client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 202)

        thanks = DivesiteCheckinThank.objects.all().first()
        self.assertTrue(thanks.is_thanked)

        payload = {
            'thank': False
        }

        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 202)

        thanks = DivesiteCheckinThank.objects.all().first()
        self.assertFalse(thanks.is_thanked)

        payload = {
            'thank': True
        }

        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 202)

        thanks = DivesiteCheckinThank.objects.all().first()
        self.assertTrue(thanks.is_thanked)
