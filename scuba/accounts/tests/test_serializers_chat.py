"""
Tests for scuba.accounts.serializers.chat.UserListSerializer.get_profile_image,
covering the switch from the DB-backed sitesettings.SystemApi.AWS_CLOUDFRONT_URL
to the settings.AWS_CLOUDFRONT env-var-backed CloudFront URL.
"""
from urllib.parse import urljoin

from django.test import SimpleTestCase

from scuba.accounts.serializers.chat import UserListSerializer
from scuba.settings import AWS_CLOUDFRONT


class TestUserListSerializerGetProfileImage(SimpleTestCase):
    def test_uses_the_settings_cloudfront_url(self):
        class FakeUser:
            @staticmethod
            def get_profile_image():
                return '/static/images/profiles/profile-blank.png'

        result = UserListSerializer.get_profile_image(FakeUser())

        expected = urljoin(AWS_CLOUDFRONT, '/static/images/profiles/profile-blank.png')
        self.assertEqual(result, expected)
