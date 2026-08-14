from io import BytesIO
from unittest import mock

from PIL import Image as PILImage

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from scuba.accounts.models import User, UserProfileImage
from scuba.settings import AWS_CLOUDFRONT


def _make_image_file(name='avatar.png', content_type='image/png'):
    buf = BytesIO()
    PILImage.new('RGB', (20, 20)).save(buf, format='PNG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type=content_type)


class TestProfileImageApi(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        self.user = User.objects.get(email='foo@nowhere.com')
        self.other_user = User.objects.get(email='test2@tester.com')

    def test_requires_authentication(self):
        response = self.client.post(
            '/api/settings/profile-image/', {'image': _make_image_file()})

        self.assertEqual(response.status_code, 401)

    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_successful_upload_returns_a_cloudfront_url(self, mock_upload):
        self.client.force_login(self.user)

        response = self.client.post(
            '/api/settings/profile-image/', {'image': _make_image_file()})

        self.assertEqual(response.status_code, 200)
        url = response.json()['profile_image']
        self.assertTrue(url.startswith(AWS_CLOUDFRONT))
        self.assertTrue(UserProfileImage.objects.filter(user=self.user).exists())

    @mock.patch('scuba.accounts.services.profile_image.S3.upload_raw_data')
    def test_upload_only_affects_the_requesting_users_own_avatar(self, mock_upload):
        self.client.force_login(self.user)

        self.client.post('/api/settings/profile-image/', {'image': _make_image_file()})

        self.assertTrue(UserProfileImage.objects.filter(user=self.user).exists())
        self.assertFalse(UserProfileImage.objects.filter(user=self.other_user).exists())

    def test_missing_image_is_rejected(self):
        self.client.force_login(self.user)

        response = self.client.post('/api/settings/profile-image/', {})

        self.assertEqual(response.status_code, 400)

    def test_unsupported_content_type_is_rejected(self):
        self.client.force_login(self.user)
        bad_file = SimpleUploadedFile('evil.txt', b'not an image', content_type='text/plain')

        response = self.client.post('/api/settings/profile-image/', {'image': bad_file})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(UserProfileImage.objects.filter(user=self.user).exists())

    def test_corrupt_file_with_spoofed_content_type_is_rejected(self):
        self.client.force_login(self.user)
        spoofed = SimpleUploadedFile('fake.png', b'not really a png', content_type='image/png')

        response = self.client.post('/api/settings/profile-image/', {'image': spoofed})

        self.assertEqual(response.status_code, 400)
