"""
Tests for scuba.accounts.forms.EmailInviteForm (CODE_REVIEW.md §3 item 2).

save() previously referenced self.user (never set in __init__) and
filtered/created UserBuddyRequest with friend=/email= kwargs that don't
exist on that model -- every call raised AttributeError/FieldError/
TypeError. The form is not wired into any live view; these are unit tests
of the form itself.
"""
from django.test import TestCase

from scuba.accounts.forms import EmailInviteForm
from scuba.accounts.models import User, UserBuddy, UserBuddyRequest


class TestEmailInviteForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='inviter@nowhere.com', username='inviteruser', password='tester1234',
            first_name='Invite', last_name='User')
        self.registered_friend = User.objects.create_user(
            email='registered@nowhere.com', username='registeredfriend',
            password='tester1234', first_name='Reg', last_name='User')

    def _form(self, email):
        form = EmailInviteForm({'email': email}, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        return form

    def test_invite_to_a_registered_user_creates_a_buddy_request(self):
        form = self._form('registered@nowhere.com')
        form.save()

        self.assertTrue(
            UserBuddyRequest.objects.filter(
                user=self.user, buddy=self.registered_friend).exists())
        self.assertEqual(form.get_email_invites(), ['registered@nowhere.com'])

    def test_invite_to_an_unregistered_email_records_it_without_a_db_row(self):
        form = self._form('notregisteredyet@nowhere.com')
        form.save()

        self.assertFalse(UserBuddyRequest.objects.filter(user=self.user).exists())
        self.assertEqual(form.get_email_invites(), ['notregisteredyet@nowhere.com'])

    def test_already_a_buddy_is_skipped(self):
        self.user.add_buddy(self.registered_friend)

        form = self._form('registered@nowhere.com')
        form.save()

        self.assertFalse(UserBuddyRequest.objects.filter(user=self.user).exists())
        self.assertEqual(form.get_email_invites(), [])

    def test_already_requested_is_skipped(self):
        UserBuddyRequest.objects.create(user=self.user, buddy=self.registered_friend)

        form = self._form('registered@nowhere.com')
        form.save()

        self.assertEqual(
            UserBuddyRequest.objects.filter(
                user=self.user, buddy=self.registered_friend).count(), 1)
        self.assertEqual(form.get_email_invites(), [])

    def test_malformed_email_in_a_comma_list_is_skipped_not_fatal(self):
        form = self._form('not-an-email, registered@nowhere.com')
        form.save()

        self.assertTrue(
            UserBuddyRequest.objects.filter(
                user=self.user, buddy=self.registered_friend).exists())
        self.assertEqual(form.get_email_invites(), ['registered@nowhere.com'])

    def test_email_invites_is_not_shared_across_instances(self):
        """ email_invites used to be a mutable class attribute, leaking
        state across every form instance/request. """
        first_form = self._form('notregisteredyet@nowhere.com')
        first_form.save()

        second_form = self._form('registered@nowhere.com')
        second_form.save()

        self.assertEqual(second_form.get_email_invites(), ['registered@nowhere.com'])
