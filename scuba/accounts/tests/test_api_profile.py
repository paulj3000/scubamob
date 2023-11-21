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


class TestProfileAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_me_profile(self):
        """
        Test me account profile
        """
        # make sure the user has to be logged in
        client = APIClient()
        response = client.get('/api/profile/me', format='json')
        self.assertEqual(response.status_code, 401)

        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        response = client.get('/api/profile/me', format='json')
        self.assertEqual(response.status_code, 200)

        profile_json = response.json().get('profile')
        self.assertTrue(profile_json['is_self'])
        self.assertIn('id', profile_json)
        self.assertEqual(profile_json['id'], user.pk_as_str)
        self.assertIn('username', profile_json)
        self.assertEqual(profile_json['username'], user.username)
        self.assertIn('buddy_count', profile_json)
        self.assertIn('profile_image', profile_json)
        self.assertEqual(profile_json['full_name'], 'First Last')

    def test_user_profile_1(self):
        """
        Test me account profile
        """
        # make sure the user has to be logged in
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test3@tester.com')
        client.force_authenticate(user=user)

        response = client.get(f'/api/profile/{user2.pk_as_str}/', format='json')
        self.assertEqual(response.status_code, 200)

        profile_json = response.json().get('profile')
        self.assertFalse(profile_json['is_self'])
        self.assertIn('id', profile_json)
        self.assertEqual(profile_json['id'], user2.pk_as_str)
        self.assertIn('username', profile_json)
        self.assertEqual(profile_json['username'], user2.username)
        self.assertIn('buddy_count', profile_json)
        self.assertEqual(profile_json['buddy_count'], 0)
        self.assertEqual(profile_json['reviews_count'], 0)
        self.assertIn('profile_image', profile_json)
        self.assertEqual(profile_json['full_name'], user2.get_full_name())
        self.assertTrue('is_self')

    def test_invalid_user_profile(self):
        """
        Test me account profile
        """
        # make sure the user has to be logged in
        client = APIClient()
        user = User.objects.get(email='foo@nowhere.com')
        client.force_authenticate(user=user)

        id = 'a' * 32

        response = client.get(f'/api/profile/{id}/', format='json')
        self.assertEqual(response.status_code, 403)

    def test_follow_profile_true(self):
        """
        Test account profile
        """
        user = User.objects.get(email='foo@nowhere.com')
        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'follow': True
        }

        response = client.post('/api/profile/d33cd081741043bc8eec98c0b047f93f/follow',
                               payload,
                               format='json')
        following = response.json()
        self.assertTrue(following['following'])

    def test_follow_profile_false(self):
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(id='d33cd081741043bc8eec98c0b047f93f')

        # set the following
        user2.set_follow_user(user, True)

        client = APIClient()
        client.force_authenticate(user=user)
        payload = {
            'follow': False
        }

        response = client.post('/api/profile/d33cd081741043bc8eec98c0b047f93f/follow',
                               payload,
                               format='json')
        following = response.json()
        self.assertFalse(following['following'])
