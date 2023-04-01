"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from scuba.accounts.models import User
from scuba.divesites.models import Divesite


class TestUserMethods(TestCase):
    fixtures = ["test_users.json", "test_divesites.json"]

    def test_user_get_full_name(self):
        """
        Test simple user get name
        """
        user = User.objects.get(email='test2@user.com')
        self.assertEqual(user.get_full_name(), "First Last")

    def test_user_is_admin_1(self):
        """
        Test simple user get name
        """
        user = User.objects.get(email='test@admin.com')

        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)

    def test_user_is_admin_2(self):
        """
        Test simple user get name
        """
        user = User.objects.get(email='test2@user.com')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)

    def test_user_add_divesite_recently_viewed(self):
        """
        Test adding a divesite to a user's recently viewed
        """
        divesite = Divesite.objects.all().first()
        user = User.objects.get(email='test2@user.com')

        obj = user.add_divesite_recently_viewed(divesite)
        viewed_date = obj.viewed_date
        obj = user.add_divesite_recently_viewed(divesite)

        self.assertNotEqual(viewed_date, obj.viewed_date)


