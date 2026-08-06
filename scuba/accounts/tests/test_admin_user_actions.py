"""
Integration tests for the admin-only reset-password and welcome-email
support URLs on scuba/accounts/admin.py's UserAdmin.
"""
from unittest.mock import patch

from django.core import mail
from django.test import TestCase

from scuba.accounts.models import User

MODEL_BACKEND = 'django.contrib.auth.backends.ModelBackend'


class TestAdminUserActionsRequireStaffLogin(TestCase):
    """ Both URLs must be unreachable by anonymous or non-staff callers. """

    def setUp(self):
        self.target = User.objects.create_user(
            email='target@user.com', username='targetuser', password='tester1234',
            first_name='Target', last_name='User')
        self.non_staff = User.objects.create_user(
            email='plain@user.com', username='plainuser', password='tester1234',
            first_name='Plain', last_name='User')

    def _reset_password_url(self, user):
        return f'/admin/accounts/user/{user.pk}/reset-password/'

    def _welcome_email_url(self, user):
        return f'/admin/accounts/user/{user.pk}/emails/welcome/'

    def test_anonymous_reset_password_is_redirected_to_login(self):
        response = self.client.get(self._reset_password_url(self.target))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_anonymous_welcome_email_is_redirected_to_login(self):
        response = self.client.get(self._welcome_email_url(self.target))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_non_staff_reset_password_is_redirected_to_login(self):
        self.client.force_login(self.non_staff, backend=MODEL_BACKEND)

        response = self.client.get(self._reset_password_url(self.target))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_non_staff_welcome_email_is_redirected_to_login(self):
        self.client.force_login(self.non_staff, backend=MODEL_BACKEND)

        response = self.client.get(self._welcome_email_url(self.target))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)


class TestAdminResetPassword(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email='staff@admin.com', username='staffadmin', password='tester1234',
            first_name='Staff', last_name='Admin', is_admin=True)
        self.target = User.objects.create_user(
            email='target@user.com', username='targetuser', password='tester1234',
            first_name='Target', last_name='User')

    def test_staff_can_trigger_password_reset_email(self):
        self.client.force_login(self.staff, backend=MODEL_BACKEND)

        response = self.client.get(f'/admin/accounts/user/{self.target.pk}/reset-password/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/admin/accounts/user/{self.target.pk}/change/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.target.email, mail.outbox[0].to)


class TestAdminWelcomeEmail(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email='staff@admin.com', username='staffadmin', password='tester1234',
            first_name='Staff', last_name='Admin', is_admin=True)
        self.target = User.objects.create_user(
            email='target@user.com', username='targetuser', password='tester1234',
            first_name='Target', last_name='User')

    @patch('scuba.libs.mail.S3')
    def test_staff_can_trigger_a_welcome_email(self, mock_s3_class):
        self.client.force_login(self.staff, backend=MODEL_BACKEND)

        response = self.client.get(f'/admin/accounts/user/{self.target.pk}/emails/welcome/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/admin/accounts/user/{self.target.pk}/change/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.target.email, mail.outbox[0].to)
        mock_s3_class.return_value.upload_data.assert_called_once()
