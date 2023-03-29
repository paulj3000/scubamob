"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User


class TestConfirmationCode(TestCase):
    @staticmethod
    def create_test_user():
        return User.objects.create(
            first_name='First',
            last_name='Last',
            date_of_birth='1970-04-01',
            email='foo@nowhere.com')

    def test_generate_confirmation_code(self):
        """
        Test generate cnfirmation codes
        """
        user = self.create_test_user()
        code1 = user.generate_confirmation_code()

        self.assertEqual(len(str(code1.code)), 6)
