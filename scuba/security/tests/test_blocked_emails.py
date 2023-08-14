"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.security.models import InvalidEmail


class TestInvalidEmails(TestCase):
    def test_email_str(self):
        """
        Test blocked email
        """
        invalid_email = InvalidEmail.objects.create(
                email='test@foo.com')

        self.assertEqual('test@foo.com', invalid_email.__str__())
