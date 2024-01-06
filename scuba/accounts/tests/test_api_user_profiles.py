"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User, UserBuddy


class TestUserProfilesAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_user_not_logged_in(self):
        """
        Test the making of a buddy request
        """
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
        profile = response.json().get('profile')

        self.assertEqual(response.status_code, 200, 'user is logged in')
        self.assertEqual(profile.get('id'), user2.pk_as_str, 'user id matches')
        self.assertEqual(profile.get('full_name'), user2.get_full_name(), 'user name matches')
        self.assertFalse(profile.get('is_private'), 'user is not private')
        # self.assertIsNotNone(profile.get('media'), 'user has media')

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
        profile_json = response.json().get('profile')

        self.assertEqual(response.status_code, 200, 'user is logged in')
        self.assertEqual(profile_json['id'], user2.pk_as_str, 'user id matches')
        self.assertEqual(profile_json['full_name'], user2.get_full_name(), 'user name matches')
        self.assertTrue(profile_json['is_private'], 'user is private')
        self.assertNotIn('location', profile_json, 'location is not visible in a private profile')

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
        profile_json = response.json().get('profile')

        self.assertEqual(response.status_code, 200, 'user is logged in')
        self.assertEqual(profile_json['id'], user2.pk_as_str, 'user id matches')
        self.assertEqual(profile_json['full_name'], user2.get_full_name(), 'user name matches')
        self.assertTrue(profile_json['is_private'], 'user is private but still friends')

    def test_get_basic_profile_is_blocked(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test4@tester.com')

        user2.block_buddy(user)

        client = APIClient()
        client.force_authenticate(user=user)
        url = f'/api/profile/{user2.pk_as_str}/'
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 403, 'blocked user not found')

    def test_get_basic_profile_is_blocked_2(self):
        """
        The blocking user should not be able to access the blockee's profile either
        """
        user = User.objects.get(email='foo@nowhere.com')
        user2 = User.objects.get(email='test4@tester.com')

        user2.block_buddy(user)

        client = APIClient()
        client.force_authenticate(user=user2)
        url = f'/api/profile/{user.pk_as_str}/'
        response = client.get(url, format='json')
        self.assertEqual(response.status_code, 403, 'blocked user not found')
