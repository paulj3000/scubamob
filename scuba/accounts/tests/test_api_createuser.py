"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import pytest
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.accounts.models import User
from scuba.accounts.serializers.signup import \
    SetUsernameSerializer, CreateUserSerializer, SetPasswordSerializer


class TestCreateUserAPI(TestCase):
    fixtures = ["test_users.json"]

    def test_create_user_1(self):
        """
        Test simple create user
        """
        client = APIClient()
        payload = {
            'first_name': "first",
            'last_name': "last",
            'date_of_birth': "1980-10-31",
            'password': "someweirdpassword",
            'email': "newuser@nowhere.com",
            'username': "newusername1"
        }

        response = client.post('/api/signup/createuser/', payload, format='json')

        id = response.json().get('id')
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(id)
        self.assertEqual(len(id), 32)
        self.assertNotIn('-', id)
        self.assertIsNotNone(response.json().get('profile_image'))
        self.assertFalse(response.json().get('confirmed'))
        self.assertEqual(response.json().get('first_name'), 'first')
        self.assertEqual(response.json().get('last_name'), 'last')
        self.assertEqual(response.json().get('confirmed'), False)
        self.assertEqual(len(response.json().get('token')), 40)

    def test_create_user_duplicate_email(self):
        """
        Test email address cannot be a duplicate
        """
        client = APIClient()
        payload = {
            'first_name': "first",
            'last_name': "last",
            'password': "someweirdpassword",
            'date_of_birth': "1980-10-31",
            'email': "foo@nowhere.com"
        }

        # call the request twice, verify the email address is already in the system
        response = client.post('/api/signup/createuser/', payload, format='json')
        response = client.post('/api/signup/createuser/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())

    def test_create_user_duplicate_username(self):
        """
        Test username cannot be a duplicate
        """
        client = APIClient()
        payload = {
            'first_name': "first",
            'last_name': "last",
            'password': "someweirdpassword",
            'date_of_birth': "1980-10-31",
            'email': "dup@duplicateusername.com",
            'username': "duplicateusername"
        }

        # call the request twice, verify the email address is already in the system
        response = client.post('/api/signup/createuser/', payload, format='json')
        self.assertEqual(response.status_code, 201)

        payload['email'] = 'foo2@nowhere.com'
        response = client.post('/api/signup/createuser/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.json())

    def test_create_user_bad_password(self):
        """
        Test password length
        """
        client = APIClient()
        payload = {
            'first_name': "first",
            'last_name': "last",
            'password': "so",
            'date_of_birth': "1980-10-31",
            'email': "foo@nowhere.com",
            'username': "username"
        }

        # call the request twice, verify the email address is already in the system
        response = client.post('/api/signup/createuser/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.json())

    def test_create_user_coppa(self):
        """
        Test user has to be at least 13 years old
        """
        twelve_years_ago = (datetime.now() - relativedelta(years=12)).strftime("%Y-%m-%d")
        client = APIClient()
        payload = {
            'first_name': "first",
            'last_name': "last",
            'password': "somewoorirdpass",
            'date_of_birth': twelve_years_ago,
            'email': "foo@nowhere.com"
        }

        # call the request twice, verify the email address is already in the system
        response = client.post('/api/signup/createuser/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('date_of_birth', response.json())

    def test_set_username(self):
        """
        Test changing username
        """
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        client.force_authenticate(user=user)

        payload = {
            'username': "anewusername"
        }

        response = client.put('/api/signup/username/', payload, format='json')
        self.assertEqual(response.status_code, 200)

    def test_set_duplicate_username(self):
        """
        Test changing username with an already taken username
        """
        user = User.objects.get(email='foo@nowhere.com')

        client = APIClient()
        payload = {
            'username': "testuser3"
        }

        response = client.put('/api/signup/username/', payload, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_implemented_1(self):
        """
        Test not implemented 1 (SetUsernameSerializer for 'create')
        """
        serializer = SetUsernameSerializer()
        with pytest.raises(NotImplementedError) as exinfo:
            raise serializer.create(None)

        # test the not implemented in create function
        self.assertIsNotNone(exinfo)

    def test_not_implemented_2(self):
        """
        Test not implemented 1 (Cr3eateUserSerializer for 'update')
        """
        serializer = CreateUserSerializer()
        with pytest.raises(NotImplementedError) as exinfo:
            raise serializer.update(None, None)

        # test the not implemented in create function
        self.assertIsNotNone(exinfo)

    def test_not_implemented_3(self):
        """
        Test not implemented 1 (SetPasswordSerializer for 'update')
        """
        serializer = SetPasswordSerializer()
        with pytest.raises(NotImplementedError) as exinfo:
            raise serializer.create(None)

        # test the not implemented in create function
        self.assertIsNotNone(exinfo)
