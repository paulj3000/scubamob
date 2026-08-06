"""
Unit tests for the impersonation service layer, run against bare requests
(not the Django admin) so the session-flush ordering and guard clauses can
be exercised directly.
"""
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from scuba.accounts.models import User
from scuba.security.models import ImpersonationEvent
from scuba.security.services import impersonation


def _request_with_session():
    request = RequestFactory().post('/irrelevant/')
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    return request


class TestImpersonationService(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            email='super@admin.com', username='superadmin', password='tester1234',
            first_name='Super', last_name='Admin', is_admin=True, is_superuser=True)
        self.target = User.objects.create_user(
            email='target@user.com', username='targetuser', password='tester1234',
            first_name='Target', last_name='User')

    def test_start_impersonation_sets_session_markers_after_login_flush(self):
        request = _request_with_session()

        event = impersonation.start_impersonation(request, self.superuser, self.target, 'debug')

        self.assertEqual(request.session['_auth_user_id'], str(self.target.pk))
        self.assertEqual(request.session[impersonation.SESSION_IMPERSONATOR_ID_KEY], str(self.superuser.pk))
        self.assertEqual(
            request.session[impersonation.SESSION_IMPERSONATION_EVENT_ID_KEY], str(event.pk))

    def test_non_superuser_actor_is_rejected(self):
        non_super = User.objects.create_user(
            email='staff@admin.com', username='staffadmin', password='tester1234',
            first_name='Staff', last_name='Admin', is_admin=True, is_superuser=False)
        request = _request_with_session()

        with self.assertRaises(impersonation.ImpersonationError):
            impersonation.start_impersonation(request, non_super, self.target, 'debug')

        self.assertFalse(ImpersonationEvent.objects.exists())

    def test_cannot_start_second_impersonation_in_same_session(self):
        request = _request_with_session()
        impersonation.start_impersonation(request, self.superuser, self.target, 'debug')

        second_target = User.objects.create_user(
            email='second@user.com', username='seconduser', password='tester1234',
            first_name='Second', last_name='User')

        with self.assertRaises(impersonation.ImpersonationError):
            impersonation.start_impersonation(request, self.superuser, second_target, 'debug again')

        self.assertEqual(ImpersonationEvent.objects.count(), 1)

    def test_stop_impersonation_restores_actor_and_closes_event(self):
        request = _request_with_session()
        event = impersonation.start_impersonation(request, self.superuser, self.target, 'debug')

        closed_event = impersonation.stop_impersonation(request)

        self.assertEqual(closed_event.pk, event.pk)
        self.assertIsNotNone(closed_event.ended_at)
        self.assertEqual(request.session['_auth_user_id'], str(self.superuser.pk))
        self.assertNotIn(impersonation.SESSION_IMPERSONATOR_ID_KEY, request.session)
        self.assertNotIn(impersonation.SESSION_IMPERSONATION_EVENT_ID_KEY, request.session)

    def test_stop_impersonation_without_active_session_raises(self):
        request = _request_with_session()

        with self.assertRaises(impersonation.ImpersonationError):
            impersonation.stop_impersonation(request)
