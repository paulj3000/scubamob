"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from rest_framework.test import APIClient
import pytest


from scuba.accounts.models import User
from scuba.divesites.models import Divesite, DivesiteCheckin


class TestFeedAPI(TestCase):
    fixtures = ["test_users.json", "test_divesites.json"]

    def test_flag_feed_invalid_id(self):
        """
        Test flag_feed true
        """
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        # these don't even match the URL's 32-hex-char pattern
        response = client.get('/api/feed/1', format='json')
        self.assertEqual(response.status_code, 404)

        response = client.get('/api/feed/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', format='json')
        self.assertEqual(response.status_code, 404)

        # these match the pattern but don't correspond to a real user --
        # CanViewProfile denies access rather than confirming non-existence,
        # consistent with how GetProfileApi and friends already behave
        response = client.get('/api/feed/1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', format='json')
        self.assertEqual(response.status_code, 403)

        response = client.get('/api/feed/70d200e9f10f4d56adc3dafd44afea2f', format='json')
        self.assertEqual(response.status_code, 403)

    def test_cannot_view_feed_of_a_user_who_blocked_you(self):
        """
        CODE_REVIEW.md §3 item 9 -- GetFeedApi must not let a blocked
        viewer see the blocking user's feed.
        """
        user = User.objects.get(email='foo@nowhere.com')
        blocker = User.objects.get(email='test3@tester.com')
        blocker.block_buddy(user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f'/api/feed/{blocker.pk_as_str}', format='json')
        self.assertEqual(response.status_code, 403)

        response = client.get(
            f'/api/profile/{blocker.pk_as_str}/feed', format='json')
        self.assertEqual(response.status_code, 403)

    def test_anonymous_checkin_does_not_leak_identity_via_profile_feed(self):
        """
        CODE_REVIEW.md §3 item 8 -- serializers/profile.py's FeedSerializer
        used to skip the is_anonymous check that serializers/feed.py's
        otherwise-identical copy already had, leaking anonymous check-in
        data through the /api/profile/<id>/feed endpoint specifically.
        """
        user = User.objects.get(email='foo@nowhere.com')
        other = User.objects.get(email='test3@tester.com')
        divesite = Divesite.objects.all().first()

        checkin = DivesiteCheckin.objects.create(
            divesite=divesite, user=other, is_anonymous=True)
        other.add_checkin_to_feed(checkin.id)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f'/api/profile/{other.pk_as_str}/feed', format='json')

        self.assertEqual(response.status_code, 200)
        feed = response.json()['feed']
        self.assertEqual(len(feed), 1)
        self.assertIsNone(feed[0]['item'])

    def test_flag_feed_empty(self):
        """
        Test flag_feed true
        """
        user = User.objects.get(email='foo@nowhere.com')
        test_user = User.objects.get(email='test3@tester.com')

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f'/api/feed/{test_user.pk_as_str}', format='json')
        self.assertEqual(response.status_code, 200)

        feed = response.json()['feed']
        self.assertEqual(len(feed), 0)

    @pytest.mark.skip(reason="This is no longer valid")
    def test_flag_feed(self):
        """
        Test flag_feed true
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.all().first()

        feed = user.add_to_feed(divesite.id, 0)

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {'is_flagged': True}

        response = client.post(f'/api/feed/{feed.pk_as_str}/flag', payload, format='json')
        self.assertEqual(response.status_code, 200)

        flagged_json = response.json()['flagged']
        self.assertTrue(flagged_json['is_flagged'])

    @pytest.mark.skip(reason="This is no longer valid")
    def test_flag_feed_false(self):
        """
        Test flag_feed false
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.all().first()

        feed = user.add_to_feed(divesite.id, 0)

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {'is_flagged': False}

        response = client.post(f'/api/feed/{feed.pk_as_str}/flag', payload, format='json')
        self.assertEqual(response.status_code, 200)

        flagged_json = response.json()['flagged']
        self.assertFalse(flagged_json['is_flagged'])

    @pytest.mark.skip(reason="This is no longer valid")
    def test_flag_feed_keep_id(self):
        """
        Test flag_feed keep id
        """
        user = User.objects.get(email='foo@nowhere.com')
        divesite = Divesite.objects.all().first()

        feed = user.add_to_feed(divesite.id, 0)
        feed_id = feed.id

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {'is_flagged': True}
        response = client.post(f'/api/feed/{feed.pk_as_str}/flag', payload, format='json')
        self.assertEqual(response.status_code, 200)

        flagged_json = response.json()['flagged']
        self.assertTrue(flagged_json['is_flagged'])

        feed2 = user.feed.all()
        self.assertEqual(feed2.count(), 1)
        self.assertEqual(feed2.first().id, feed_id)

        payload = {'is_flagged': False}
        response = client.post(f'/api/feed/{feed.pk_as_str}/flag', payload, format='json')
        self.assertEqual(response.status_code, 200)

        flagged_json = response.json()['flagged']
        self.assertFalse(flagged_json['is_flagged'])

        feed3 = user.feed.all()
        self.assertEqual(feed3.count(), 1)
        self.assertEqual(feed3.first().id, feed_id)

        payload = {'is_flagged': True}
        response = client.post(f'/api/feed/{feed.pk_as_str}/flag', payload, format='json')
        self.assertEqual(response.status_code, 200)

        flagged_json = response.json()['flagged']
        self.assertTrue(flagged_json['is_flagged'])

        feed4 = user.feed.all()
        self.assertEqual(feed4.count(), 1)
        self.assertEqual(feed4.first().id, feed_id)
