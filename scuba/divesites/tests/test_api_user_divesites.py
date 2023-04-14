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
