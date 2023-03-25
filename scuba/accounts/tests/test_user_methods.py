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
