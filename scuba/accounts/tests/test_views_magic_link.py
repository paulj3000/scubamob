from unittest.mock import patch

from freezegun import freeze_time

from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from scuba.accounts.models import MagicLinkToken, User
from scuba.accounts.services import magiclink


class TestMagicLinkRequestView(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        cache.clear()

    def test_request_page_renders(self):
        response = self.client.get('/login/magic-link/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/magic_link_request.html')

    @patch('scuba.libs.mail.S3')
    def test_request_for_known_user_creates_token_and_sends_email(self, mock_s3_class):
        user = User.objects.get(email='foo@nowhere.com')

        response = self.client.post('/login/magic-link/', {'email': user.email})

        self.assertRedirects(response, '/login/magic-link/sent/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.email, mail.outbox[0].to)
        self.assertEqual(MagicLinkToken.objects.filter(user=user).count(), 1)
        mock_s3_class.return_value.upload_data.assert_called_once()

    @patch('scuba.libs.mail.S3')
    def test_request_for_unknown_email_does_not_reveal_and_sends_nothing(self, mock_s3_class):
        response = self.client.post('/login/magic-link/', {'email': 'nobody@nowhere.com'})

        self.assertRedirects(response, '/login/magic-link/sent/')
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(MagicLinkToken.objects.exists())
        mock_s3_class.return_value.upload_data.assert_not_called()

    @patch('scuba.libs.mail.S3')
    def test_request_for_inactive_user_sends_nothing(self, mock_s3_class):
        user = User.objects.get(email='foo@nowhere.com')
        user.is_active = False
        user.save()

        response = self.client.post('/login/magic-link/', {'email': user.email})

        self.assertRedirects(response, '/login/magic-link/sent/')
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(MagicLinkToken.objects.filter(user=user).exists())

    @patch('scuba.libs.mail.S3')
    def test_repeated_requests_only_leave_one_live_token(self, mock_s3_class):
        user = User.objects.get(email='foo@nowhere.com')

        self.client.post('/login/magic-link/', {'email': user.email})
        self.client.post('/login/magic-link/', {'email': user.email})

        self.assertEqual(MagicLinkToken.objects.filter(user=user).count(), 2)
        self.assertEqual(MagicLinkToken.objects.filter(user=user, redeemed=False).count(), 1)

    @patch('scuba.libs.mail.S3')
    def test_request_is_rate_limited_per_email(self, mock_s3_class):
        user = User.objects.get(email='foo@nowhere.com')

        for _ in range(5):
            response = self.client.post('/login/magic-link/', {'email': user.email})
            self.assertRedirects(response, '/login/magic-link/sent/')

        self.assertEqual(len(mail.outbox), 3)


class TestMagicLinkConfirmView(TestCase):
    fixtures = ["test_users.json"]

    def setUp(self):
        cache.clear()
        self.user = User.objects.get(email='foo@nowhere.com')

    def test_valid_token_logs_user_in_and_redeems_it(self):
        token, raw_token = magiclink.create_magic_link_token(self.user)
        url = magiclink.build_magic_link_url(self.user, raw_token)
        path = url.replace('http://localhost:8000', '')

        response = self.client.get(path)

        self.assertRedirects(response, '/home', fetch_redirect_response=False)
        self.assertTrue('_auth_user_id' in self.client.session)

        token.refresh_from_db()
        self.assertTrue(token.redeemed)

    def test_token_is_single_use(self):
        token, raw_token = magiclink.create_magic_link_token(self.user)
        url = magiclink.build_magic_link_url(self.user, raw_token)
        path = url.replace('http://localhost:8000', '')

        self.client.get(path)
        self.client.logout()

        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/magic_link_invalid.html')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_expired_token_is_rejected(self):
        with freeze_time(timezone.now()) as frozen:
            _, raw_token = magiclink.create_magic_link_token(self.user)
            url = magiclink.build_magic_link_url(self.user, raw_token)
            path = url.replace('http://localhost:8000', '')

            frozen.tick(delta=timezone.timedelta(minutes=16))

            response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/magic_link_invalid.html')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_garbage_uidb64_and_token_are_rejected(self):
        response = self.client.get('/login/magic-link/not-a-real-uid/not-a-real-token/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/magic_link_invalid.html')

    def test_inactive_user_cannot_use_a_valid_token(self):
        self.user.is_active = False
        self.user.save()

        _, raw_token = magiclink.create_magic_link_token(self.user)
        url = magiclink.build_magic_link_url(self.user, raw_token)
        path = url.replace('http://localhost:8000', '')

        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/magic_link_invalid.html')
        self.assertFalse('_auth_user_id' in self.client.session)
