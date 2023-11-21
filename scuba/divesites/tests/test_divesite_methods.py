"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import date

from django.test import TestCase

from scuba.divesites.models import Divesite
from scuba.accounts.models import User


class TestDivesiteMethods(TestCase):
    fixtures = ["test_divesites.json", "test_users.json", "test_sitesettings.json"]

    def test_new_divesite_object(self):
        """
        Verify if a divesite, upon saving, gets a new url
        """
        new_ds = Divesite.objects.create(
            name='Whites Point2',
            description='some description',
            difficulty=0,
            lat=0.00,
            long=0.00)
        self.assertEqual(new_ds.url, "whites-point2")

        # change the name
        new_ds.name = 'whites2-point2'
        new_ds.save()
        self.assertEqual(new_ds.url, "whites2-point2")

    def test_divesite_stats(self):
        """
        get the stats for a particular divesite
        """
        divesite = Divesite.objects.all().first()
        users = User.objects.all()
        user0 = users[0]
        user1 = users[1]
        user2 = users[2]

        today = date.today()

        divesite.stats.create(
            user=user0,
            temp_c=26.67,
            visibility=48.8,
            stats_date=today)

        divesite.stats.create(
            user=user1,
            temp_c=24.32,
            visibility=51.3,
            stats_date=today)

        divesite.stats.create(
            user=user2,
            temp_c=32.21,
            visibility=45.2,
            stats_date=today)

        stats = divesite.get_divesite_stats(today)

        self.assertEqual(stats['avg_temp_f'], 81)
        self.assertEqual(stats['avg_visibility'], 48)
        self.assertEqual(stats['avg_temp_c'], 27)

    def test_divesite_string(self):
        """
        test the name of the divesite
        """
        divesite = Divesite.objects.filter(name='White Point').first()
        self.assertEqual(divesite.__str__(), 'White Point')

    def test_get_active_divesites(self):
        """
        test getting active divesites
        """
        active_divesites = Divesite.get_all_active_divesites()
        self.assertEqual(len(active_divesites), 1)

    def test_generate_aws_id(self):
        """
        test generation of an aws_id
        """
        id = Divesite.generate_aws_id()
        self.assertTrue(id.startswith('dx'))
        self.assertEqual(id[4], '/')

    def test_divesite_has_aws_id(self):
        """
        verify the divesite has a valid id
        """
        divesite = Divesite.objects.all().first()
        self.assertIsNotNone(divesite.aws_id)
