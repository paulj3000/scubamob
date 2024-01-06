"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from django.test.client import Client

from scuba.libs.authentication.usernameauthentication import UsernameAuthentication
from scuba.accounts.models import User


class TestUsernameAuthentication(TestCase):
    fixtures = ["test_users.json"]

    def test_username(self):
        """
        Validating the login by way of username works
        """
        client = Client()
        response = client.get("/api/login/")
        auth = UsernameAuthentication()

        request = response.wsgi_request
        result = auth.authenticate(request, 'testusernamefoo', 'password')
        self.assertIsNotNone(result)

    def test_username2(self):
        """
        Validating the login by way of username works by way of kwargs
        """
        client = Client()
        response = client.get("/api/login/")
        auth = UsernameAuthentication()

        request = response.wsgi_request

        kwargs = {
            'username': 'testuser2x',
            'password': 'password',
        }
        result = auth.authenticate(request, **kwargs)
        self.assertIsNotNone(result)

    def test_bad_username(self):
        '''
        Validating a bad login by way of username
        '''
        client = Client()
        response = client.get("/api/signup/createuser/")
        admin = UsernameAuthentication()

        request = response.wsgi_request
        result = admin.authenticate(request, 'badusername', 'tester1234')
        self.assertIsNone(result)

    def test_username_bad_password(self):
        """
        Validating the login by way of username with bad password
        """
        client = Client()
        response = client.get("/api/login/")
        auth = UsernameAuthentication()

        request = response.wsgi_request
        result = auth.authenticate(request, 'testusernamefoo', 'badpassword')
        self.assertIsNone(result)

    def test_get_user(self):
        """
        Testing the "get_user" function
        """
        auth = UsernameAuthentication()

        user = User.objects.get(username='testusernamefoo')
        self.assertIsNotNone(auth.get_user(user.id))

    def test_get_user_with_bad_id(self):
        """
        Testing the "get_user" function
        """
        auth = UsernameAuthentication()
        self.assertIsNone(auth.get_user('861bf455a6234ea69da8814493d9faaa'))
