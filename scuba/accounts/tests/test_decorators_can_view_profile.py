"""
Tests for scuba.accounts.decorators.can_view_profile (CODE_REVIEW.md §3
item 11 -- it never checked profile.is_private).

ViewProfile is a managed=False model backed by a DB view that doesn't
exist in the test database (a separate, already-tracked issue -- see
TASK_TRACKER.md's Known Technical Debt on "view_profile"). To test this
decorator's logic without that dependency, get_object_or_404 (the only
call that would touch ViewProfile) is mocked to return a lightweight
stand-in; User and UserBuddy lookups run against the real test DB.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.http import Http404
from django.test import RequestFactory, TestCase

from scuba.accounts.decorators import can_view_profile
from scuba.accounts.models import User, UserBuddy


def _fake_profile(user, is_active=True, is_hidden=False, is_private=False):
    return SimpleNamespace(
        pk_as_str=user.pk_as_str, id=user.id,
        is_active=is_active, is_hidden=is_hidden, is_private=is_private)


class TestCanViewProfile(TestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(
            email='viewer@nowhere.com', username='viewer', password='tester1234',
            first_name='Viewer', last_name='User')
        self.target = User.objects.create_user(
            email='target@nowhere.com', username='targetuser', password='tester1234',
            first_name='Target', last_name='User')
        self.factory = RequestFactory()
        self.view_func = MagicMock(return_value='view result')

    def _call(self, profile):
        with patch('scuba.accounts.decorators.get_object_or_404', return_value=profile):
            request = self.factory.get(f'/p/{self.target.username}')
            request.user = self.viewer
            wrapped = can_view_profile(self.view_func)
            return wrapped(request, username=self.target.username)

    def test_private_profile_is_blocked_for_non_buddies(self):
        profile = _fake_profile(self.target, is_private=True)

        with self.assertRaises(Http404):
            self._call(profile)

    def test_private_profile_is_visible_to_buddies(self):
        UserBuddy.objects.create(user=self.target, buddy=self.viewer)
        profile = _fake_profile(self.target, is_private=True)

        result = self._call(profile)

        self.assertEqual(result, 'view result')

    def test_public_profile_is_visible_to_non_buddies(self):
        profile = _fake_profile(self.target, is_private=False)

        result = self._call(profile)

        self.assertEqual(result, 'view result')

    def test_inactive_profile_is_still_blocked(self):
        """ regression check: the is_private fix must not have disturbed
        the pre-existing is_active/is_hidden checks. """
        profile = _fake_profile(self.target, is_active=False)

        with self.assertRaises(Http404):
            self._call(profile)
