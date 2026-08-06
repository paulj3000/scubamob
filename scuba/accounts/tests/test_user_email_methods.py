"""
Tests for User.send_confirmation_code_email/generate_confirmation_code_email
and User.send_welcome_email/generate_welcome_email (CODE_REVIEW.md §3 item 4).

These used to depend on an EmailTemplate model that doesn't exist anywhere
in the codebase; reworked to generate subject/content directly instead of
loading it from a DB-backed template (Option B). S3 (used by
scuba.libs.mail.store_email to archive a copy of every sent email) is
mocked -- no live AWS access. Django's test runner automatically swaps
EMAIL_BACKEND for the locmem backend, so django.core.mail.outbox works
without touching real SES.
"""
from unittest.mock import patch

from django.core import mail
from django.test import TestCase

from scuba.accounts.models import User


class TestSendConfirmationCodeEmail(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='confirm@nowhere.com', username='confirmuser', password='tester1234',
            first_name='Confirm', last_name='User')

    @patch('scuba.libs.mail.S3')
    def test_sends_an_email_containing_the_code(self, mock_s3_class):
        self.user.send_confirmation_code_email(123456)

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn(self.user.email, sent.to)
        self.assertIn('123456', sent.subject)
        mock_s3_class.return_value.upload_data.assert_called_once()

    def test_generate_returns_html_and_text_versions(self):
        html, text = self.user.generate_confirmation_code_email(654321)

        self.assertIn('654321', html)
        self.assertIn('654321', text)
        # the text version must not contain the raw html tags
        self.assertNotIn('<strong>', text)


class TestSendWelcomeEmail(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='welcome@nowhere.com', username='welcomeuser', password='tester1234',
            first_name='Wel', last_name='Come')

    @patch('scuba.libs.mail.S3')
    def test_sends_an_email(self, mock_s3_class):
        self.user.send_welcome_email()

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertIn(self.user.email, sent.to)
        mock_s3_class.return_value.upload_data.assert_called_once()

    def test_generate_returns_html_and_text_versions_with_the_users_name(self):
        html, text = self.user.generate_welcome_email()

        self.assertIn('Wel Come', html)
        self.assertIn('Wel Come', text)
