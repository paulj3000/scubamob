"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from rest_framework.test import APIClient


SNS_PAYLOAD = {
    "Type": "SubscriptionConfirmation",
    "MessageId": "XXXXXXXX-1ee3-4de3-9c69-XXXXXXXXXXXX",
    "Token": "SECRET_TOKEN",
    "TopicArn": "arn:aws:sns:us-west-2:XXXXXXXXXXXX:ses-test",
    "Message": "You have chosen to subscribe to the topic arn:aws:sns:us-west-2:XXXXXXXXXXXX:ses-test. To confirm the subscription, visit the SubscribeURL included in this message.",  # noqa: E501
    "SubscribeURL": "https://sns.us-west-2.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-west-2:XXXXXXXXXXXX:ses-test&Token=SECRET_TOKEN",  # noqa: E501
    "Timestamp": "2018-11-21T19:48:08.170Z",
    "SignatureVersion": "1",
    "Signature": "SECRET",
    "SigningCertURL": "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.pem"  # noqa: E501
}


class TestBlockedEmail(TestCase):
    def test_subscription_request(self):
        """
        Test subscription request
        """

        client = APIClient()
        response = client.post('/security/emails/bounced', SNS_PAYLOAD, format='json')
        self.assertEqual(response.status_code, 201)

    def test_subscription_request_failed(self):
        # noqa: E501
        """
        Test subscription request
        """

        client = APIClient()
        response = client.post('/security/emails/bounced', SNS_PAYLOAD, format='json')
        self.assertEqual(response.status_code, 201)

        response = client.post('/security/emails/bounced', SNS_PAYLOAD, format='json')
        self.assertEqual(response.status_code, 400)
