"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import pytest

from django.test import TestCase

from scuba.accounts.serializers.password import PasswordResetSerializer


class TestAccountPasswordSerializer(TestCase):
    def test_create(self):
        """
        Test the serializer trying to "create"
        """
        serializer = PasswordResetSerializer()
        with pytest.raises(NotImplementedError):
            serializer.create({})

    def test_update(self):
        """
        Test the serializer trying to "update"
        """
        serializer = PasswordResetSerializer()
        with pytest.raises(NotImplementedError):
            serializer.update({}, {})
