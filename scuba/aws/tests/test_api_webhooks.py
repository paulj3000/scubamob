"""
Integration tests for the AWS CodeBuild/CodePipeline SNS webhook endpoints.
Both must reject any message that doesn't carry a valid AWS SNS signature.
"""
from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework.test import APIClient

from scuba.libs.aws.testing import generate_test_keypair_and_cert, sign_sns_payload

VALID_CERT_URL = 'https://sns.us-west-2.amazonaws.com/SimpleNotificationService-abc123.pem'


def _subscription_confirmation_payload(topic_suffix):
    return {
        'Type': 'SubscriptionConfirmation',
        'MessageId': f'msg-{topic_suffix}',
        'Token': 'token-value',
        'TopicArn': f'arn:aws:sns:us-west-2:123456789012:{topic_suffix}',
        'Message': 'You have chosen to subscribe...',
        'SubscribeURL': (
            f'https://sns.us-west-2.amazonaws.com/?Action=ConfirmSubscription&'
            f'TopicArn=arn:aws:sns:us-west-2:123456789012:{topic_suffix}&Token=token-value'),
        'Timestamp': '2026-08-06T00:00:00.000Z',
        'SignatureVersion': '1',
        'SigningCertURL': VALID_CERT_URL,
    }


class _WebhookTestBase(TestCase):
    __test__ = False  # collected only via the concrete subclasses below

    endpoint = None
    topic_suffix = None

    def setUp(self):
        self.private_key, self.cert_pem = generate_test_keypair_and_cert()
        self.client = APIClient()

    def _mock_cert_response(self):
        response = Mock()
        response.content = self.cert_pem
        response.raise_for_status = Mock()
        return response

    def test_message_from_an_untrusted_signing_host_is_rejected(self):
        payload = _subscription_confirmation_payload(self.topic_suffix)
        payload['SigningCertURL'] = 'https://evil.example.com/cert.pem'
        payload['Signature'] = 'not-a-real-signature'

        response = self.client.post(self.endpoint, payload, format='json')

        self.assertEqual(response.status_code, 403)

    @patch('scuba.libs.aws.sns.requests.get')
    def test_message_with_a_forged_signature_is_rejected(self, mock_get):
        mock_get.return_value = self._mock_cert_response()
        payload = _subscription_confirmation_payload(self.topic_suffix)
        payload['Signature'] = 'not-a-real-signature'

        response = self.client.post(self.endpoint, payload, format='json')

        self.assertEqual(response.status_code, 403)

    @patch('scuba.libs.aws.sns.requests.get')
    def test_validly_signed_subscription_confirmation_is_accepted(self, mock_get):
        mock_get.return_value = self._mock_cert_response()
        payload = sign_sns_payload(
            self.private_key, _subscription_confirmation_payload(self.topic_suffix))

        response = self.client.post(self.endpoint, payload, format='json')

        self.assertEqual(response.status_code, 201)


class TestCodeBuildWebhook(_WebhookTestBase):
    __test__ = True
    endpoint = '/aws/cicd/build'
    topic_suffix = 'codebuild-topic'


class TestCodePipelineWebhook(_WebhookTestBase):
    __test__ = True
    endpoint = '/aws/cicd/pipeline'
    topic_suffix = 'codepipeline-topic'
