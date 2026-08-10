"""
Tests for scuba.home.apis.GetHomescreenApi. Weather calls are mocked -- no
live WeatherAPI access.
"""
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User

WEATHER_PAYLOAD = {
    'location': {'name': 'Ocean Beach', 'region': 'California', 'country': 'USA'},
    'current': {'temp_f': 68},
}


class TestHomeAPI(TestCase):
    fixtures = ["test_divesites.json", "test_users.json", "test_sitesettings.json"]

    def setUp(self):
        cache.clear()

    @patch('scuba.home.apis.Weather.get_current_by_q_param')
    def test_homescreen_calls_weather_api_once_then_uses_cache(self, mock_weather):
        mock_weather.return_value = dict(WEATHER_PAYLOAD)

        user = User.objects.get(email='foo@nowhere.com')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/home/?q=92107', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_weather.call_count, 1)

        # a second request for the same q_param must be served from the
        # cache -- the external Weather API must not be called again.
        mock_weather.return_value = dict(WEATHER_PAYLOAD)
        response = client.get('/api/home/?q=92107', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_weather.call_count, 1)
