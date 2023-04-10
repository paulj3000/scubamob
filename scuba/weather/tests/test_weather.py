"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from copy import deepcopy

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.weather.models import Weather
from scuba.libs.exceptions import InvalidWeatherDataException

# new data object
data = {
    'location': {
        'name': 'Omaha',
        'region': 'Nebraska',
        'country': 'USA',
        'lat': '41.2565',
        'lon': '-95.9345',
        'tz_id': 'UTC/GMT',
        'localtime_epoch': 10000,
        'data': {"some": "key"},
    }
}

class TestWeather(TestCase):
    fixtures = ["test_weather.json", "google_settings.json"]

    def test_weather_by_lat_lng(self):
        """
        Test weater locations by lat, lng. Specifically, test distance
        """
        # test by point loma with a distance of 1
        items = Weather.get_current_by_lat_lng(32.73501, -117.24107, 1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, 'San Diego')

        # test by point loma with a distance of 20 miles, should include all
        # san diego
        items = Weather.get_current_by_lat_lng(32.73501, -117.24107, 20)
        self.assertEqual(len(items), 3)
        for item in items:
            self.assertEqual(item.name, 'San Diego')

        # test by point loma with a distance of 100, should include all
        # san diego and san clemente
        items = Weather.get_current_by_lat_lng(32.73501, -117.24107, 100)
        self.assertEqual(len(items), 6)
        for item in items:
            self.assertIn(item.name, ['San Diego', 'San Clemente'])


        # test by point loma with a distance of 200, should include
        # san diego, san clemente, malibu, la canada flintridge, pasadena, malibu
        items = Weather.get_current_by_lat_lng(32.73501, -117.24107, 200)
        self.assertEqual(len(items), 11)
        for item in items:
            self.assertIn(
                item.name,
                ['San Diego', 'San Clemente', 'Pasadena', 'La Canada Flintridge',
                 'Malibu'])

    def test_weather_by_postal_code(self):
        # test by point loma with a distance of 200, should include
        # san diego, san clemente, malibu, la canada flintridge, pasadena, malibu
        items = Weather.get_current_by_postal_code(92107, 1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, 'San Diego')

        items = Weather.get_current_by_postal_code(92107, 20)
        self.assertEqual(len(items), 3)
        for item in items:
            self.assertEqual(item.name, 'San Diego')

    def test_add_good_data(self):
        # make sure the data went in
        Weather.add_weather_data(data)
        items = Weather.get_current_by_lat_lng(41.2565, -95.9345)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, 'Omaha')

    def test_bad_data(self):

        bd1 = deepcopy(data)
        bd1.pop('location')
        with self.assertRaises(InvalidWeatherDataException):
            Weather.add_weather_data(bd1)

        remove_keys = [
            'name', 'region', 'country', 'lat', 'lon', 'tz_id', 'localtime_epoch']

        for akey in remove_keys:
            bd = deepcopy(data)
            bd['location'].pop(akey)
            with self.assertRaises(InvalidWeatherDataException, msg=f"testing against '{akey}'"):
                Weather.add_weather_data(bd)
