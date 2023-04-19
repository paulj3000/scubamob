"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import date
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.divesites.models import Divesite


class TestUserAccountsAPI(TestCase):
    fixtures = ["test_divesites.json", "test_users.json", "test_sitesettings.json"]

    def test_get_reviews(self):
        """
        Test the making of a buddy request
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


        client = APIClient()
        client.force_authenticate(user=user2)
        url = f'/api/divesites/{divesite.pk_as_str}/reviews/'
        response = client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f'/api/accounts/reviews'
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 200)

        reviews = response.json().get('reviews')
        self.assertIsNotNone(reviews)

        # verify there is one review
        self.assertEqual(len(reviews), 1, "There should only be one review")
