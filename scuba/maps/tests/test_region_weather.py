from unittest import mock

from django.test import TestCase

from scuba.libs.exceptions import InvalidCoordinatesException, InvalidWeatherDataException
from scuba.maps.models import Region


class TestGetWeatherByLatLong(TestCase):
    @mock.patch('scuba.maps.models.Weather.get_current_by_lat_lng')
    def test_valid_coordinates_calls_weather_api(self, mock_get_current):
        mock_get_current.return_value = {
            'location': {'name': 'San Diego', 'region': 'California', 'country': 'USA'},
            'current': {'temp_f': 70},
        }

        weather, region = Region.get_weather_by_lat_long(32.7157, -117.1611)

        mock_get_current.assert_called_once_with(32.7157, -117.1611)
        self.assertEqual(weather['current']['temp_f'], 70)
        self.assertEqual(region.name, 'SAN DIEGO')

    @mock.patch('scuba.maps.models.Weather.get_current_by_lat_lng')
    def test_out_of_range_latitude_is_rejected_without_calling_the_api(self, mock_get_current):
        with self.assertRaises(InvalidCoordinatesException):
            Region.get_weather_by_lat_long(95, -117.1611)

        mock_get_current.assert_not_called()

    @mock.patch('scuba.maps.models.Weather.get_current_by_lat_lng')
    def test_out_of_range_longitude_is_rejected_without_calling_the_api(self, mock_get_current):
        with self.assertRaises(InvalidCoordinatesException):
            Region.get_weather_by_lat_long(32.7157, -190)

        mock_get_current.assert_not_called()

    @mock.patch('scuba.maps.models.Weather.get_current_by_lat_lng')
    def test_non_numeric_coordinates_are_rejected(self, mock_get_current):
        with self.assertRaises(InvalidCoordinatesException):
            Region.get_weather_by_lat_long('not-a-lat', -117.1611)

        mock_get_current.assert_not_called()

    def test_invalid_coordinates_exception_is_caught_by_existing_weather_handlers(self):
        self.assertTrue(issubclass(InvalidCoordinatesException, InvalidWeatherDataException))
