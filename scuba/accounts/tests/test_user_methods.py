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

    def test_user_is_premier(self):
        """
        Test simple user get name
        """
        user = User.objects.get(email='test@tester.com')
        self.assertEqual(hasattr(user, 'userispremier'), False)
        self.assertEqual(user.is_premier, False)

        user.set_is_premier(True)
        user = User.objects.get(email='test@tester.com')
        self.assertEqual(hasattr(user, 'userispremier'), True)
        self.assertEqual(user.is_premier, True)

        user.set_is_premier(False)
        user = User.objects.get(email='test@tester.com')
        self.assertEqual(hasattr(user, 'userispremier'), False)
        self.assertEqual(user.is_premier, False)

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

    def test_user_add_divesite_to_favorite(self):
        """
        Add a divesite to user's favorite list
        """
        divesite = Divesite.objects.all().first()
        user = User.objects.get(email='test2@user.com')

        user.set_divesite_favorite(divesite)
        favorite = user.divesites_favorites.filter(divesite=divesite)
        self.assertIsNotNone(favorite)

        # make sure there is only one record for this divesite
        user.divesites_favorites.filter(divesite=divesite)
        user.divesites_favorites.filter(divesite=divesite)
        user.divesites_favorites.filter(divesite=divesite)
        favorites = user.divesites_favorites.filter(divesite=divesite)
        self.assertEqual(favorites.count(), 1)

    def test_user_remove_divesite_from_favorites(self):
        """
        Remove a divesite from user's favorite list
        """
        divesite = Divesite.objects.all().first()
        user = User.objects.get(email='test2@user.com')

        # make sure it got into the database
        user.set_divesite_favorite(divesite)
        favorite = user.divesites_favorites.filter(divesite=divesite)
        self.assertIsNotNone(favorite)

        # now remove it
        user.set_divesite_favorite(divesite, False)
        favorites = user.divesites_favorites.filter(divesite=divesite)
        self.assertEqual(favorites.count(), 0)
