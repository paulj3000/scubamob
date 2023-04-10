"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.weather.models import Weather


class TestWeather(TestCase):
    fixtures = ["test_weather.json"]

    def test_weather_by_lat_long(self):
        """
        Test weater locations by lat, long. Specifically, test distance
        """
        # test by point loma with a distance of 1
        items = Weather.get_current_by_lat_long(32.73501, -117.24107, 1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].name, 'San Diego')

        # test by point loma with a distance of 20 miles, should include all
        # san diego
        items = Weather.get_current_by_lat_long(32.73501, -117.24107, 20)
        self.assertEqual(len(items), 3)
        for item in items:
            self.assertEqual(item.name, 'San Diego')

        # test by point loma with a distance of 100, should include all
        # san diego and san clemente
        items = Weather.get_current_by_lat_long(32.73501, -117.24107, 100)
        self.assertEqual(len(items), 6)
        for item in items:
            self.assertIn(item.name, ['San Diego', 'San Clemente'])


        # test by point loma with a distance of 200, should include
        # san diego, san clemente, malibu, la canada flintridge, pasadena, malibu
        items = Weather.get_current_by_lat_long(32.73501, -117.24107, 200)
        self.assertEqual(len(items), 11)
        for item in items:
            self.assertIn(
                item.name,
                ['San Diego', 'San Clemente', 'Pasadena', 'La Canada Flintridge',
                 'Malibu'])
