"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import date
from io import BytesIO
from unittest import mock

from PIL import Image

from django.core.exceptions import ValidationError
from django.test import TestCase

from scuba.divesites.models import Divesite
from scuba.accounts.models import User
from scuba.settings import AWS_CLOUDFRONT


class TestDivesiteMethods(TestCase):
    fixtures = ["test_divesites.json", "test_users.json"]

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

    def test_duplicate_name_gets_unique_url(self):
        """
        Two divesites with the same name should not collide on url
        """
        first = Divesite.objects.create(
            name='Duplicate Point',
            description='first',
            difficulty=0,
            lat=0.00,
            long=0.00)
        second = Divesite.objects.create(
            name='Duplicate Point',
            description='second',
            difficulty=0,
            lat=0.00,
            long=0.00)

        self.assertEqual(first.url, 'duplicate-point')
        self.assertEqual(second.url, 'duplicate-point-2')

    def test_lat_long_out_of_range_fails_validation(self):
        """
        Latitude/longitude outside valid ranges should fail model validation
        """
        divesite = Divesite(
            name='Out Of Range',
            description='invalid coords',
            difficulty=0,
            lat=95.0,
            long=0.0)

        with self.assertRaises(ValidationError):
            divesite.full_clean()

    def test_get_local_divesites_filters_by_distance(self):
        """
        get_local_divesites should only return divesites within range
        """
        near = Divesite.objects.create(
            name='Near Point',
            description='near',
            difficulty=0,
            lat=33.72,
            long=-118.31)

        far = Divesite.objects.create(
            name='Far Point',
            description='far',
            difficulty=0,
            lat=51.5074,
            long=-0.1278)

        nearby = Divesite.get_local_divesites(lat=33.714741100, lng=-118.314238300, distance=50)
        nearby_names = set(nearby.values_list('name', flat=True))

        self.assertIn('White Point', nearby_names)
        self.assertIn(near.name, nearby_names)
        self.assertNotIn(far.name, nearby_names)

    def test_get_local_divesites_without_params_returns_all_active(self):
        """
        Missing lat/lng/distance should fall back to all active divesites
        """
        result = Divesite.get_local_divesites(None, None, None)
        self.assertEqual(
            set(result.values_list('id', flat=True)),
            set(Divesite.get_all_active_divesites().values_list('id', flat=True)))

    def test_upload_banner_sets_active_banner(self):
        """
        Uploading a banner should create a retrievable DivesiteBanner
        """
        divesite = Divesite.objects.filter(name='White Point').first()

        image = BytesIO()
        Image.new('RGB', (10, 10)).save(image, format='PNG')
        image.seek(0)

        with mock.patch('scuba.libs.imageuploader.S3.upload_raw_data'):
            divesite.upload_banner(image)

        self.assertEqual(divesite.banners.count(), 1)
        self.assertTrue(divesite.banners.get().is_active)
        self.assertIn(AWS_CLOUDFRONT, divesite.get_active_banner())
