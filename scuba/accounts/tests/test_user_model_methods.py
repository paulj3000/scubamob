"""
Tests for three User model methods fixed under CODE_REVIEW.md §3 items
3, 5, 6. All three had zero call sites anywhere in the app (confirmed via
grep) -- these are landmine fixes, not fixes to anything live.
"""
import base64
from unittest.mock import patch

from django.test import TestCase

from scuba.accounts.models import User, UserBuddyRequest, UserProfileImage, UserSetting


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


def _data_uri_for(raw_bytes, ext='png'):
    encoded = base64.urlsafe_b64encode(raw_bytes).decode('ascii')
    return f'data:image/{ext};base64,{encoded}'


class TestUploadProfileImageAsString(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='profileimage@nowhere.com', username='profileimageuser',
            password='tester1234', first_name='Profile', last_name='User')

    def test_invalid_input_returns_none(self):
        result = self.user.upload_profile_image_as_string('not a data uri')

        self.assertIsNone(result)

    @patch('scuba.accounts.models.S3.upload_raw_data')
    def test_creates_a_new_profile_image(self, mock_upload):
        data_uri = _data_uri_for(b'fake-png-bytes')

        profile_image = self.user.upload_profile_image_as_string(data_uri)

        self.assertIsInstance(profile_image, UserProfileImage)
        self.assertEqual(profile_image.user, self.user)
        self.assertTrue(profile_image.image.startswith(f'profiles/{self.user.aws_id}/'))

        mock_upload.assert_called_once()
        args, kwargs = mock_upload.call_args
        self.assertEqual(args[0], profile_image.image)
        self.assertEqual(args[1], b'fake-png-bytes')
        self.assertEqual(kwargs['ContentType'], 'image/png')

    @patch('scuba.accounts.models.S3.upload_raw_data')
    def test_replaces_an_existing_profile_image(self, mock_upload):
        existing = UserProfileImage.objects.create(user=self.user, image='profiles/old.png')

        data_uri = _data_uri_for(b'new-bytes')
        profile_image = self.user.upload_profile_image_as_string(data_uri)

        self.assertEqual(profile_image.pk, existing.pk)
        self.assertNotEqual(profile_image.image, 'profiles/old.png')
        self.assertEqual(UserProfileImage.objects.filter(user=self.user).count(), 1)
