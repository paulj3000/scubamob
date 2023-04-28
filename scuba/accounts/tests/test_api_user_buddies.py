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


class TestUserBuddiesAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_add_buddy_request(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user_to_add = User.objects.get(email='addbuddy@tester.com')
        user_to_add_private = User.objects.get(email='test4@tester.com')

        payload = {
            'buddy_id': user_to_add.pk_as_str
        }

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/buddies/add/', payload, format='json')
        self.assertEqual(response.status_code, 201)

        # let's test if a private account can be added
        user_to_add_private.is_private = True
        user_to_add_private.save()

        payload = {
            'buddy_id': user_to_add_private.pk_as_str
        }

        response = client.post('/api/buddies/add/', payload, format='json')
        self.assertEqual(response.status_code, 404, 'Cannot add a private account')

    def test_remove_buddy_request(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user_to_remove = User.objects.get(email='addbuddy@tester.com')

        # first, add the user in the buddy table
        user.add_buddy(user_to_remove)

        payload = {
            'buddy_id': user_to_remove.pk_as_str
        }

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/buddies/remove/', payload, format='json')
        self.assertEqual(response.status_code, 202, 'Successfully remove a user')

        # make sure the buddy does not exist in the user's records
        self.assertIsNone(user.get_buddy(user_to_remove))
        self.assertIsNotNone(user.removed.filter(buddy=user_to_remove).first())

    def test_block_buddy_request(self):
        """
        Test the blocking of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        buddy = User.objects.get(email='test@tester.com')

        client = APIClient()
        client.force_authenticate(user=user)

        url = f'/api/buddies/{buddy.pk_as_str}/block/'

        response = client.post(url, format='json')
        self.assertEqual(response.status_code, 202)

        # now try to add the user again
        payload = {
            'buddy_id': buddy.pk_as_str
        }

        response = client.post('/api/buddies/add/', payload, format='json')
        self.assertEqual(response.status_code, 404)

    def test_accept_buddy_request(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user1 = User.objects.get(email='test@tester.com')
        request = user1.add_buddy_request(user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(f'/api/buddies/requests/{request.pk_as_str}/accept', format='json')
        self.assertEqual(response.status_code, 201)
        accept = response.json()
        self.assertIn('accept', accept)

    def test_blocked_buddy_request(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')
        user1 = User.objects.get(email='test@tester.com')
        request = user1.add_buddy_request(user)

        # block the buddy
        user1.block_buddy(user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(f'/api/buddies/requests/{request.pk_as_str}/accept', format='json')
        self.assertEqual(response.status_code, 400)

    def test_add_bad_buddy_id_request(self):
        """
        Test the making of a buddy request
        """
        user = User.objects.get(email='foo@nowhere.com')

        # this is a bad / unknown UUID
        payload = {
            'buddy_id': 'be79448e87094b0f81b7c5d3b59d518e'
        }

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/buddies/add/', payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_listing_buddies(self):
        """
        Test the listing of user's buddies
        """
        user = User.objects.get(email='foo@nowhere.com')
        user1 = User.objects.get(email='test@tester.com')
        user2 = User.objects.get(email='test2@tester.com')

        user.add_buddy(user1)
        user.add_buddy(user2)

        # and query for the divesites
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/buddies/', format='json')
        self.assertEqual(response.status_code, 200)
        the_list = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('buddies', the_list)
        self.assertEqual(len(the_list['buddies']), 2)

        for i in range(0, 2):
            self.assertIn('id', the_list['buddies'][i])
            self.assertIn('profile_image', the_list['buddies'][i])
            self.assertIn('full_name', the_list['buddies'][i])

    def test_listing_buddy_requests(self):
        """
        Test the listing of user's buddies
        """
        user = User.objects.get(email='foo@nowhere.com')
        user1 = User.objects.get(email='test@tester.com')
        user2 = User.objects.get(email='test2@tester.com')

        user.add_buddy_request(user1)
        user.add_buddy_request(user2)

        # and query for the divesites
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/buddies/requests/', format='json')
        self.assertEqual(response.status_code, 200)
        the_list = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn('requests', the_list)
        self.assertEqual(len(the_list['requests']), 2)

        for i in range(0, 2):
            self.assertIn('id', the_list['requests'][i])
            self.assertIn('profile_image', the_list['requests'][i])
            self.assertIn('full_name', the_list['requests'][i])

    def test_follow_buddy_request(self):
        """
        Test the following of a buddy
        """
        user = User.objects.get(email='foo@nowhere.com')
        buddy = User.objects.get(email='test@tester.com')

        user.add_buddy(buddy)

        payload = {
            'follow': False
        }

        client = APIClient()
        client.force_authenticate(user=user)
        url = f'/api/buddies/{buddy.pk_as_str}/follow/'
        response = client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 202)

        # check if the follow flag is NOT set
        user_buddy = user.buddies.get(buddy=buddy)
        self.assertFalse(user_buddy.is_following)

        payload = {
            'follow': True
        }

        # now follow the buddy
        response = client.put(url, payload, format='json')
        self.assertEqual(response.status_code, 202)

        # ...and check if the follow flag is set
        user_buddy = user.buddies.get(buddy=buddy)
        self.assertTrue(user_buddy.is_following)
