"""
Integration tests for the audited "login as user" admin support tool.
"""
from django.test import TestCase

from scuba.accounts.models import User
from scuba.security.models import ImpersonationEvent

MODEL_BACKEND = 'django.contrib.auth.backends.ModelBackend'


class TestAdminImpersonation(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            email='super@admin.com', username='superadmin', password='tester1234',
            first_name='Super', last_name='Admin', is_admin=True, is_superuser=True)
        self.staff_non_super = User.objects.create_user(
            email='staff@admin.com', username='staffadmin', password='tester1234',
            first_name='Staff', last_name='Admin', is_admin=True, is_superuser=False)
        self.other_superuser = User.objects.create_user(
            email='other@admin.com', username='othersuper', password='tester1234',
            first_name='Other', last_name='Admin', is_admin=True, is_superuser=True)
        self.target = User.objects.create_user(
            email='target@user.com', username='targetuser', password='tester1234',
            first_name='Target', last_name='User')

    def _impersonate_url(self, user):
        return f'/admin/accounts/user/{user.pk}/impersonate/'

    def test_superuser_can_start_impersonation(self):
        self.client.force_login(self.superuser, backend=MODEL_BACKEND)

        response = self.client.post(
            self._impersonate_url(self.target), {'reason': 'debugging a support ticket'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        event = ImpersonationEvent.objects.get()
        self.assertEqual(event.actor, self.superuser)
        self.assertEqual(event.target, self.target)
        self.assertEqual(event.reason, 'debugging a support ticket')
        self.assertIsNone(event.ended_at)

        session = self.client.session
        self.assertEqual(session['_auth_user_id'], str(self.target.pk))
        self.assertEqual(session['impersonator_id'], str(self.superuser.pk))
        self.assertEqual(session['impersonation_event_id'], str(event.pk))

    def test_non_superuser_staff_is_blocked(self):
        self.client.force_login(self.staff_non_super, backend=MODEL_BACKEND)

        response = self.client.post(
            self._impersonate_url(self.target), {'reason': 'debugging a support ticket'})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(ImpersonationEvent.objects.exists())

        session = self.client.session
        self.assertEqual(session['_auth_user_id'], str(self.staff_non_super.pk))

    def test_cannot_impersonate_a_superuser(self):
        self.client.force_login(self.superuser, backend=MODEL_BACKEND)

        response = self.client.post(
            self._impersonate_url(self.other_superuser), {'reason': 'debugging'})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(ImpersonationEvent.objects.exists())

        session = self.client.session
        self.assertEqual(session['_auth_user_id'], str(self.superuser.pk))

    def test_reason_is_required(self):
        self.client.force_login(self.superuser, backend=MODEL_BACKEND)

        response = self.client.post(self._impersonate_url(self.target), {'reason': '   '})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(ImpersonationEvent.objects.exists())

    def test_cannot_impersonate_self(self):
        self.client.force_login(self.superuser, backend=MODEL_BACKEND)

        response = self.client.post(
            self._impersonate_url(self.superuser), {'reason': 'debugging'})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(ImpersonationEvent.objects.exists())

    def test_stop_impersonation_restores_original_admin(self):
        self.client.force_login(self.superuser, backend=MODEL_BACKEND)
        self.client.post(self._impersonate_url(self.target), {'reason': 'debugging'})

        response = self.client.post('/impersonate/stop/')

        self.assertEqual(response.status_code, 302)

        session = self.client.session
        self.assertEqual(session['_auth_user_id'], str(self.superuser.pk))
        self.assertNotIn('impersonator_id', session)
        self.assertNotIn('impersonation_event_id', session)

        event = ImpersonationEvent.objects.get()
        self.assertIsNotNone(event.ended_at)

    def test_stop_impersonation_without_active_session_is_a_no_op(self):
        self.client.force_login(self.target, backend=MODEL_BACKEND)

        response = self.client.post('/impersonate/stop/')

        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session['_auth_user_id'], str(self.target.pk))

    def test_get_renders_confirmation_form(self):
        self.client.force_login(self.superuser, backend=MODEL_BACKEND)

        response = self.client.get(self._impersonate_url(self.target))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.target.email)
