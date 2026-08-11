"""
Tests for scuba.libs.external.google_address.GoogleAddress. The googlemaps
client is mocked -- no live Google Maps API access.
"""
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase

from scuba.libs.external.google_address import GoogleAddress
from scuba.settings import GOOGLE_API_KEY


class TestGoogleAddress(SimpleTestCase):
    @patch('scuba.libs.external.google_address.googlemaps.Client')
    def test_get_geocode_from_postal_code_uses_settings_key(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.geocode.return_value = [{'geometry': {'location': {}}}]
        mock_client_cls.return_value = mock_client

        GoogleAddress.get_geocode_from_postal_code('92107')

        mock_client_cls.assert_called_once_with(key=GOOGLE_API_KEY)

    @patch('scuba.libs.external.google_address.googlemaps.Client')
    def test_get_geocode_from_postal_code_returns_client_result(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.geocode.return_value = [{'geometry': {'location': {'lat': 1, 'lng': 2}}}]
        mock_client_cls.return_value = mock_client

        result = GoogleAddress.get_geocode_from_postal_code('92107')

        mock_client.geocode.assert_called_once_with('92107')
        self.assertEqual(result, mock_client.geocode.return_value)
