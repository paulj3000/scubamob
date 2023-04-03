"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.divesites.models import Divesite


class TestUserBuddiesAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_add_buddy_request(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user_to_add = User.objects.get(email='addbuddy@tester.com')

        payload = {
            'buddy_id': user_to_add.pk_as_str
        }

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/user/buddies/add/', payload, format='json')
        self.assertEqual(response.status_code, 201)

    def test_add_bad_buddy_id_request(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')

        payload = {
            'buddy_id': 'be79448e87094b0f81b7c5d3b59d518e'
        }

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/user/buddies/add/', payload, format='json')
        self.assertEqual(response.status_code, 400)

    '''
    def add_buddy_request(self, buddy):
        obj, created = self.buddy_requests.update_or_create(
            buddy=buddy,
            defaults={'is_active': True},
        )

        #if created:
        #    Alerting.send_buddy_request(self.pk_as_str, buddy.pk_as_str)


        payload = {
            'divesite_id': divesite.pk_as_str
        }

        client = APIClient()
        response = client.post('/api/user/divesites/favorites/', payload, format='json')
        self.assertEqual(response.status_code, 202)

        # nope, the user needs to be logged in
        self.assertEqual(response.status_code, 401)
    '''
