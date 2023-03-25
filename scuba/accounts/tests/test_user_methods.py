"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase

from scuba.accounts.models import User


class TestUserMethods(TestCase):
    def test_user_get_full_name(self):
        """
        Test simple user get name
        """
        user = User.objects.create(
            first_name='First',
            last_name='Last',
            date_of_birth='1970-01-01',
            email='test@user.com')
        user.set_password('password')
        user.save()
        self.assertEqual(user.get_full_name(), "First Last")

    def test_user_is_admin_1(self):
        """
        Test simple user get name
        """
        user = User.objects.create(
            first_name='First',
            last_name='Last',
            is_admin=True,
            date_of_birth='1970-01-01',
            email='test@user.com')
        user.set_password('password')
        user.save()

        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)

    def test_user_is_admin_2(self):
        """
        Test simple user get name
        """
        user = User.objects.create(
            first_name='First',
            last_name='Last',
            date_of_birth='1970-01-01',
            email='test2@user.com')
        user.set_password('password')
        user.save()

        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
