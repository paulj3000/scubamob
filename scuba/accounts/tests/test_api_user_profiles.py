"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import date
from dateutil.relativedelta import relativedelta

import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User, UserBuddy, UserBlocked


class TestUserProfilesAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_user_not_logged_in(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test4@tester.com')

        client = APIClient()
        url = f'/api/profile/{user2.pk_as_str}/'
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 401, 'user is not logged in')

    def test_get_basic_profile_is_not_private(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test4@tester.com')

        user2.is_private = False
        user2.save()

        client = APIClient()
        client.force_authenticate(user=user)
        url = f'/api/profile/{user2.pk_as_str}/'
        response = client.get(url, format='json')
        profile = response.json()

        self.assertEqual(response.status_code, 200, 'user is logged in')
        self.assertEqual(profile.get('id'), user2.pk_as_str, 'user id matches')
        self.assertEqual(profile.get('full_name'), user2.get_full_name(), 'user name matches')
        self.assertIsNone(profile.get('is_private'), 'user is not private')
        self.assertIsNotNone(profile.get('media'), 'user has media')

    def test_get_basic_profile_is_private(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test4@tester.com')

        user2.is_private = True
        user2.save()

        client = APIClient()
        client.force_authenticate(user=user)
        url = f'/api/profile/{user2.pk_as_str}/'
        response = client.get(url, format='json')
        profile = response.json()

        self.assertEqual(response.status_code, 200, 'user is logged in')
        self.assertEqual(profile.get('id'), user2.pk_as_str, 'user id matches')
        self.assertEqual(profile.get('full_name'), user2.get_full_name(), 'user name matches')
        self.assertIsNotNone(profile.get('is_private'), 'user is not private')
        self.assertIsNone(profile.get('media'), 'user has media')

    def test_get_basic_profile_is_private_but_buddies(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test4@tester.com')

        user2.is_private = True
        user2.save()

        UserBuddy.objects.create(user=user, buddy=user2)
        UserBuddy.objects.create(user=user2, buddy=user)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f'/api/profile/{user2.pk_as_str}/'
        response = client.get(url, format='json')
        profile = response.json()

        self.assertEqual(response.status_code, 200, 'user is logged in')
        self.assertEqual(profile.get('id'), user2.pk_as_str, 'user id matches')
        self.assertEqual(profile.get('full_name'), user2.get_full_name(), 'user name matches')
        self.assertIsNone(profile.get('is_private'), 'user is private but still friends')
        self.assertIsNotNone(profile.get('media'), 'user has media')

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_get_basic_profile_is_blocked(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test4@tester.com')

        user2.is_private = True
        user2.save()

        UserBlocked.objects.create(user=user2, buddy=user, blocked_by=user2)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f'/api/profile/{user2.pk_as_str}/'
        response = client.get(url, format='json')
        profile = response.json()

        import  pprint
        pprint.pprint(profile)

        pprint.pprint(UserBlocked.objects.filter(buddy=user))


        f = open("/tmp/demofile2.txt", "a")
        f.write(pprint.pformat(profile, indent=4))
        f.close()

        self.assertEqual(response.status_code, 404, 'blocked user not found')
