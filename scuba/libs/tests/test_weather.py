"""
Tests for scuba.libs.weather.Weather. All requests.get calls are mocked --
no live WeatherAPI access.
"""
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase, TestCase

from scuba.libs.weather import Weather, WEATHER_API, REQUEST_TIMEOUT_SECONDS
from scuba.libs.exceptions import InvalidWeatherDataException
from scuba.settings import WEATHER_API_KEY


class TestWeatherUrls(SimpleTestCase):
    def test_weather_api_urls_are_https(self):
        self.assertTrue(WEATHER_API['current'].startswith('https://'))
        self.assertTrue(WEATHER_API['forecast'].startswith('https://'))


class TestWeather(TestCase):
    @patch('scuba.libs.weather.requests.get')
    def test_get_api_key_reads_from_settings(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {'ok': True})

        Weather.get_current_by_q_param('92107')

        self.assertEqual(mock_get.call_args[0][1]['key'], WEATHER_API_KEY)

    @patch('scuba.libs.weather.requests.get')
    def test_get_current_by_q_param_passes_timeout(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {'ok': True})

        Weather.get_current_by_q_param('92107')

        self.assertEqual(mock_get.call_args.kwargs['timeout'], REQUEST_TIMEOUT_SECONDS)

    @patch('scuba.libs.weather.requests.get')
    def test_get_current_by_lat_lng_passes_timeout(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {'ok': True})

        Weather.get_current_by_lat_lng(32.7, -117.2)

        self.assertEqual(mock_get.call_args.kwargs['timeout'], REQUEST_TIMEOUT_SECONDS)

    @patch('scuba.libs.weather.requests.get')
    def test_get_current_by_postal_code_passes_timeout(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {'ok': True})

        Weather.get_current_by_postal_code('92107')

        self.assertEqual(mock_get.call_args.kwargs['timeout'], REQUEST_TIMEOUT_SECONDS)

    @patch('scuba.libs.weather.requests.get')
    def test_get_current_by_postal_code_raises_on_error_status(self, mock_get):
        mock_get.return_value = MagicMock(status_code=400, json=lambda: {})

        with self.assertRaises(InvalidWeatherDataException):
            Weather.get_current_by_postal_code('bogus')

    @patch('scuba.libs.weather.requests.get')
    def test_get_current_by_q_param_raises_on_error_status(self, mock_get):
        mock_get.return_value = MagicMock(status_code=500, json=lambda: {})

        with self.assertRaises(InvalidWeatherDataException):
            Weather.get_current_by_q_param('bogus')
