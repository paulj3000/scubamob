"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import pytest
from django.test import TestCase

import scuba.libs.exceptions as libs_exceptions


class TestExceptions(TestCase):
    def test_invalidhttpstatuscode(self):
        """
        test the invalidhttpstatuscode
        """
        InvalidHttpStatusCode = libs_exceptions.InvalidHttpStatusCode
        with pytest.raises(InvalidHttpStatusCode) as exinfo:
            raise InvalidHttpStatusCode(404, 'not found')

        self.assertEqual(str(exinfo.value), 'not found')
        self.assertEqual(exinfo.typename, 'InvalidHttpStatusCode')

    def test_chatserverdownexception(self):
        """
        test the chatserverdownexception
        """
        ChatServerDownException = libs_exceptions.ChatServerDownException
        with pytest.raises(ChatServerDownException) as exinfo:
            raise ChatServerDownException('chat server down')

        self.assertEqual(str(exinfo.value), 'chat server down')
        self.assertEqual(exinfo.typename, 'ChatServerDownException')

    def test_invalidweatherdataexception(self):
        """
        test the invalidweatherdataexception
        """
        InvalidWeatherDataException = libs_exceptions.InvalidWeatherDataException
        with pytest.raises(InvalidWeatherDataException) as exinfo:
            raise InvalidWeatherDataException('bad weather data')

        self.assertEqual(str(exinfo.value), 'bad weather data')
        self.assertEqual(exinfo.typename, 'InvalidWeatherDataException')
