"""
Tests for scuba.libs.context_processors.scuba.Scuba.
"""
from unittest.mock import patch

from django.test import TestCase, RequestFactory

from scuba.accounts.models import User
from scuba.libs.context_processors.scuba import Scuba


class TestScubaContextProcessor(TestCase):
    fixtures = ["test_users.json", "test_sitesettings.json"]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(email='foo@nowhere.com')

    def _request(self):
        request = self.factory.get('/')
        request.user = self.user

        # RequestFactory requests have no session middleware applied
        from django.contrib.sessions.backends.db import SessionStore
        request.session = SessionStore()
        return request

    @patch('scuba.accounts.models.User.get_profile_image')
    def test_uses_session_cached_profile_image_without_recalculating(self, mock_get_image):
        """
        If profile_image is already cached in the session, the context
        processor must not call get_profile_image() again -- .get() with a
        default would evaluate the default eagerly on every request,
        defeating the cache.
        """
        request = self._request()
        request.session['profile_image'] = 'cached-image-url.png'

        context = Scuba(request)

        self.assertEqual(context['profile_image'], 'cached-image-url.png')
        mock_get_image.assert_not_called()

    @patch('scuba.accounts.models.User.get_profile_image', return_value='fresh-image-url.png')
    def test_calls_get_profile_image_when_not_cached(self, mock_get_image):
        request = self._request()

        context = Scuba(request)

        self.assertEqual(context['profile_image'], 'fresh-image-url.png')
        mock_get_image.assert_called_once()
