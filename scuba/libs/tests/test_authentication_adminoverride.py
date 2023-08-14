"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import uuid

from django.test import TestCase
from django.test.client import RequestFactory
from django.test.client import Client

from scuba.libs.authentication.adminoverride import AdminOverride
from scuba.accounts.models import User


class TestAdminOverride(TestCase):
    fixtures = ["test_users.json"]

    def test_admin_override(self):
        """
        Validating the login from a superuser works
        """
        client = Client()
        response = client.get("/api/signup/createuser/")
        admin = AdminOverride()

        request = response.wsgi_request
        result = admin.authenticate(request, 'foo@nowhere.com', 'test@admin.com%tester1234')
        self.assertIsNotNone(result)
        self.assertIsNotNone(request.session.get('adminoverride'))

        # try with a non-admin user
        response = client.get("/api/signup/createuser/")
        admin = AdminOverride()

        request = response.wsgi_request
        result = admin.authenticate(request, 'foo@nowhere.com', 'test@tester.com%tester1234')
        self.assertIsNone(result)
        self.assertIsNone(request.session.get('adminoverride'))

        kwargs = {
            'email': 'foo@nowhere.com',
            'password': 'test@admin.com%tester1234'
        }
        result = admin.authenticate(request, **kwargs)
        self.assertIsNotNone(result)
        self.assertIsNotNone(request.session.get('adminoverride'))

    def test_admin_invalid_user(self):
        """
        Validating the login from a superuser works
        """
        client = Client()
        response = client.get("/api/signup/createuser/")
        admin = AdminOverride()

        request = response.wsgi_request
        result = admin.authenticate(request, 'foox@nowhere.com', 'test@admin.com%tester1234')
        self.assertIsNone(result, 'Test bad admin override')
        self.assertIsNone(request.session.get('adminoverride'))

        request = response.wsgi_request
        result = admin.authenticate(request, 'foox@nowhere.com', 'test@admin.com%tester1234')
        self.assertIsNone(result, 'Test admin override without a "%"')
        self.assertIsNone(request.session.get('adminoverride'))

    def test_get_user(self):
        """
        Validating the login from a superuser works
        """
        client = Client()
        response = client.get("/api/signup/createuser/")
        admin = AdminOverride()

        user = User.objects.get(email='foo@nowhere.com')

        request = response.wsgi_request
        result = admin.get_user(user.id)
        self.assertIsNotNone(result)

    def test_get_user_dne(self):
        """
        Validating the login from a superuser works
        """
        client = Client()
        response = client.get("/api/signup/createuser/")
        admin = AdminOverride()

        user = User.objects.get(email='foo@nowhere.com')

        request = response.wsgi_request
        result = admin.get_user(uuid.uuid4())
        self.assertIsNone(result)
