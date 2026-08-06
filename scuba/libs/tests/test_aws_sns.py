"""
Unit tests for scuba.libs.aws.sns.verify_signature (AWS SNS webhook
signature verification). No live network calls: requests.get is mocked
wherever the code under test would otherwise fetch a real certificate.
"""
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from scuba.libs.aws.sns import SNSVerificationError, verify_signature
from scuba.libs.aws.testing import generate_test_keypair_and_cert, sign_sns_payload

VALID_CERT_URL = 'https://sns.us-west-2.amazonaws.com/SimpleNotificationService-abc123.pem'


def _notification_payload():
    return {
        'Type': 'Notification',
        'MessageId': 'msg-1',
        'TopicArn': 'arn:aws:sns:us-west-2:123456789012:test-topic',
        'Message': '{"hello": "world"}',
        'Timestamp': '2026-08-06T00:00:00.000Z',
        'SignatureVersion': '1',
        'SigningCertURL': VALID_CERT_URL,
    }


class TestVerifySignature(SimpleTestCase):
    def setUp(self):
        self.private_key, self.cert_pem = generate_test_keypair_and_cert()

    def _mock_cert_response(self):
        response = Mock()
        response.content = self.cert_pem
        response.raise_for_status = Mock()
        return response

    @patch('scuba.libs.aws.sns.requests.get')
    def test_validly_signed_message_passes(self, mock_get):
        mock_get.return_value = self._mock_cert_response()
        payload = sign_sns_payload(self.private_key, _notification_payload())

        verify_signature(payload)  # should not raise

    @patch('scuba.libs.aws.sns.requests.get')
    def test_tampered_message_body_is_rejected(self, mock_get):
        mock_get.return_value = self._mock_cert_response()
        payload = sign_sns_payload(self.private_key, _notification_payload())
        payload['Message'] = '{"hello": "tampered"}'

        with self.assertRaises(SNSVerificationError):
            verify_signature(payload)

    @patch('scuba.libs.aws.sns.requests.get')
    def test_signature_from_a_different_keypair_is_rejected(self, mock_get):
        mock_get.return_value = self._mock_cert_response()
        other_private_key, _ = generate_test_keypair_and_cert()
        payload = sign_sns_payload(other_private_key, _notification_payload())

        with self.assertRaises(SNSVerificationError):
            verify_signature(payload)

    def test_signing_cert_url_on_an_untrusted_host_is_rejected(self):
        payload = _notification_payload()
        payload['SigningCertURL'] = 'https://evil.example.com/cert.pem'
        payload['Signature'] = 'irrelevant'

        with self.assertRaises(SNSVerificationError):
            verify_signature(payload)

    def test_signing_cert_url_over_plain_http_is_rejected(self):
        payload = _notification_payload()
        payload['SigningCertURL'] = 'http://sns.us-west-2.amazonaws.com/cert.pem'
        payload['Signature'] = 'irrelevant'

        with self.assertRaises(SNSVerificationError):
            verify_signature(payload)

    def test_missing_signature_is_rejected(self):
        payload = _notification_payload()  # has no "Signature" key

        with self.assertRaises(SNSVerificationError):
            verify_signature(payload)

    def test_missing_required_field_is_rejected(self):
        payload = _notification_payload()
        payload['Signature'] = 'placeholder'
        del payload['TopicArn']

        with self.assertRaises(SNSVerificationError):
            verify_signature(payload)
