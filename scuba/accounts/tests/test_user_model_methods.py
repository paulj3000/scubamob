"""
Tests for User model methods fixed under CODE_REVIEW.md §3 items 3 and 5.
Both had zero call sites anywhere in the app (confirmed via grep) --
these are landmine fixes, not fixes to anything live.
"""
import uuid

from django.test import TestCase

from scuba.accounts.models import User, UserBuddyRequest, UserFeed, UserProfileImage, UserSetting
from scuba.settings import AWS_CLOUDFRONT


class TestGetSetting(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='settings@nowhere.com', username='settingsuser', password='tester1234',
            first_name='Settings', last_name='User')

    def test_creates_a_default_on_first_lookup(self):
        setting = self.user.get_setting('dark-mode')

        self.assertIsInstance(setting, UserSetting)
        self.assertEqual(setting.user, self.user)
        self.assertTrue(UserSetting.objects.filter(user=self.user).exists())

    def test_returns_the_existing_row_on_subsequent_lookups(self):
        first = self.user.get_setting('dark-mode')
        second = self.user.get_setting('dark-mode')

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(UserSetting.objects.filter(user=self.user).count(), 1)


class TestGetActiveBuddyRequests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='recipient@nowhere.com', username='recipientuser', password='tester1234',
            first_name='Recipient', last_name='User')
        self.requester = User.objects.create_user(
            email='requester@nowhere.com', username='requesteruser', password='tester1234',
            first_name='Requester', last_name='User')

    def test_returns_active_requests_sent_to_this_user(self):
        UserBuddyRequest.objects.create(user=self.requester, buddy=self.user, is_active=True)

        requests = self.user.get_active_buddy_requests()

        self.assertEqual(list(requests), list(
            UserBuddyRequest.objects.filter(buddy=self.user, is_active=True)))
        self.assertEqual(requests.count(), 1)

    def test_excludes_inactive_requests(self):
        UserBuddyRequest.objects.create(user=self.requester, buddy=self.user, is_active=False)

        requests = self.user.get_active_buddy_requests()

        self.assertEqual(requests.count(), 0)

    def test_excludes_requests_sent_by_this_user(self):
        UserBuddyRequest.objects.create(user=self.user, buddy=self.requester, is_active=True)

        requests = self.user.get_active_buddy_requests()

        self.assertEqual(requests.count(), 0)


class TestUserProfileImageUrl(TestCase):
    """
    UserProfileImage.get_profile_image() used to run the S3 key through
    Django's static() tag and strip a stray 'programs/' prefix that
    doesn't match anything the app ever writes -- the resulting URL
    (/static/profiles/...) was never servable. It should build a
    CloudFront URL and strip the 'profiles/' prefix the upload path
    actually uses, matching every other S3-backed image field in the app
    (e.g. DivesiteBanner.get_banner_image).
    """
    def setUp(self):
        self.user = User.objects.create_user(
            email='avatarurl@nowhere.com', username='avatarurluser',
            password='tester1234', first_name='Avatar', last_name='User')

    def test_returns_a_cloudfront_url_with_the_profiles_prefix_stripped(self):
        image = UserProfileImage.objects.create(
            user=self.user, image='profiles/abc123/xyz_1700000000.jpg')

        self.assertEqual(
            image.get_profile_image(), f"{AWS_CLOUDFRONT}abc123/xyz_1700000000.jpg")

    def test_user_get_profile_image_delegates_to_it(self):
        UserProfileImage.objects.create(user=self.user, image='profiles/abc123/xyz.jpg')

        self.assertEqual(self.user.get_profile_image(), f"{AWS_CLOUDFRONT}abc123/xyz.jpg")


class TestGetBuddiesFeed(TestCase):
    """
    Tests for User.get_buddies_feed, added for the homepage "friends
    activity" dashboard widget.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            email='feedowner@nowhere.com', username='feedowneruser',
            password='tester1234', first_name='Feed', last_name='Owner')
        self.buddy = User.objects.create_user(
            email='feedbuddy@nowhere.com', username='feedbuddyuser',
            password='tester1234', first_name='Feed', last_name='Buddy')
        self.stranger = User.objects.create_user(
            email='feedstranger@nowhere.com', username='feedstrangeruser',
            password='tester1234', first_name='Feed', last_name='Stranger')

        self.user.add_buddy(self.buddy)

    def test_includes_only_buddies_activity(self):
        buddy_entry = UserFeed.objects.create(
            user=self.buddy, instance_type=1, instance_id=uuid.uuid4())
        UserFeed.objects.create(
            user=self.stranger, instance_type=1, instance_id=uuid.uuid4())

        feed = self.user.get_buddies_feed()

        self.assertEqual(list(feed), [buddy_entry])

    def test_excludes_private_entries(self):
        UserFeed.objects.create(
            user=self.buddy, instance_type=0, instance_id=uuid.uuid4(), is_private=True)

        self.assertEqual(list(self.user.get_buddies_feed()), [])

    def test_orders_most_recent_first_and_respects_limit(self):
        first = UserFeed.objects.create(
            user=self.buddy, instance_type=1, instance_id=uuid.uuid4())
        second = UserFeed.objects.create(
            user=self.buddy, instance_type=1, instance_id=uuid.uuid4())

        feed = list(self.user.get_buddies_feed(limit=1))

        self.assertEqual(feed, [second])
        self.assertNotIn(first, feed)
