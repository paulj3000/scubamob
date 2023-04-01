"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from scuba.divesites.models import Divesite


class TestDivesiteMethods(TestCase):
    def test_new_divesite_object(self):
        """
        Verify if a divesite, upon saving, gets a new url
        """
        new_ds = Divesite.objects.create(
            name='Whites Point',
            description='some description',
            difficulty=0,
            lat=0.00,
            long=0.00)
        self.assertEqual(new_ds.url, "whites-point")

        # change the name
        new_ds.name = 'whites2-point2'
        new_ds.save()
        self.assertEqual(new_ds.url, "whites2-point2")
