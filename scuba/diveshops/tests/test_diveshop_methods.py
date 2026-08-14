from django.test import TestCase

from scuba.diveshops.models import Diveshop


class TestGetLocalDiveshops(TestCase):
    def setUp(self):
        # roughly Long Beach, CA
        self.nearby = Diveshop.objects.create(
            name='Nearby Shop', lat=33.767, long=-118.19, is_active=True)
        # roughly New York, NY -- far away
        self.far = Diveshop.objects.create(
            name='Far Shop', lat=40.7128, long=-74.006, is_active=True)
        self.inactive_nearby = Diveshop.objects.create(
            name='Inactive Nearby Shop', lat=33.767, long=-118.19, is_active=False)

    def test_filters_by_distance_and_active(self):
        nearby = Diveshop.get_local_diveshops(lon=-118.2437, lat=34.0522, radius=50)

        self.assertIn(self.nearby, nearby)
        self.assertNotIn(self.far, nearby)
        self.assertNotIn(self.inactive_nearby, nearby)

    def test_without_params_returns_all_active(self):
        result = Diveshop.get_local_diveshops(None, None, None)

        self.assertIn(self.nearby, result)
        self.assertIn(self.far, result)
        self.assertNotIn(self.inactive_nearby, result)
