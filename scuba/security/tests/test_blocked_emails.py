"""
Integration tests for the /security/emails/bounced SNS webhook. Every
message must carry a valid AWS SNS signature to be accepted.
"""
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.libs.aws.testing import generate_test_keypair_and_cert, sign_sns_payload

VALID_CERT_URL = 'https://sns.us-west-2.amazonaws.com/SimpleNotificationService-abc123.pem'

SNS_PAYLOAD = {
    "Type": "SubscriptionConfirmation",
    "MessageId": "XXXXXXXX-1ee3-4de3-9c69-XXXXXXXXXXXX",
    "Token": "SECRET_TOKEN",
    "TopicArn": "arn:aws:sns:us-west-2:XXXXXXXXXXXX:ses-test",
    "Message": "You have chosen to subscribe to the topic arn:aws:sns:us-west-2:XXXXXXXXXXXX:ses-test. To confirm the subscription, visit the SubscribeURL included in this message.",  # noqa: E501
    "SubscribeURL": "https://sns.us-west-2.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-west-2:XXXXXXXXXXXX:ses-test&Token=SECRET_TOKEN",  # noqa: E501
    "Timestamp": "2018-11-21T19:48:08.170Z",
    "SignatureVersion": "1",
    "SigningCertURL": VALID_CERT_URL,
}


class TestBlockedEmail(TestCase):
    def setUp(self):
        self.private_key, self.cert_pem = generate_test_keypair_and_cert()
        self.client = APIClient()

    def _mock_cert_response(self):
        response = Mock()
        response.content = self.cert_pem
        response.raise_for_status = Mock()
        return response

    def test_unsigned_subscription_request_is_rejected(self):
        """ a message with no valid AWS SNS signature must never be accepted """
        payload = dict(SNS_PAYLOAD, Signature='SECRET')

        response = self.client.post('/security/emails/bounced', payload, format='json')

        self.assertEqual(response.status_code, 403)

    @patch('scuba.libs.aws.sns.requests.get')
    def test_validly_signed_subscription_request(self, mock_get):
        mock_get.return_value = self._mock_cert_response()
        payload = sign_sns_payload(self.private_key, dict(SNS_PAYLOAD))

        response = self.client.post('/security/emails/bounced', payload, format='json')

        self.assertEqual(response.status_code, 201)

    @patch('scuba.libs.aws.sns.requests.get')
    def test_validly_signed_subscription_request_rejects_duplicate(self, mock_get):
        mock_get.return_value = self._mock_cert_response()

        first = sign_sns_payload(self.private_key, dict(SNS_PAYLOAD))
        response = self.client.post('/security/emails/bounced', first, format='json')
        self.assertEqual(response.status_code, 201)

        second = sign_sns_payload(self.private_key, dict(SNS_PAYLOAD))
        response = self.client.post('/security/emails/bounced', second, format='json')
        self.assertEqual(response.status_code, 400)
