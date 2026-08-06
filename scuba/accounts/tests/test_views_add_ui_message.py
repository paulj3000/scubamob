"""
Tests for scuba.accounts.views.profiles.AddUIMessageView (CODE_REVIEW.md
§3 item 17 -- request.get('message') isn't a real HttpRequest method, and
JsonResponse() requires a data argument). Not wired to any URL, so tested
directly via RequestFactory.
"""
import json

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from scuba.accounts.models import User
from scuba.accounts.views.profiles import AddUIMessageView


class TestAddUIMessageView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='uimessage@nowhere.com', username='uimessageuser', password='tester1234',
            first_name='UI', last_name='User')
        self.factory = RequestFactory()

    def _post(self, data):
        request = self.factory.post('/whatever/', data)
        request.user = self.user
        request.session = self.client.session
        setattr(request, '_messages', FallbackStorage(request))
        return AddUIMessageView.as_view()(request)

    def test_with_a_message_returns_valid_json(self):
        response = self._post({'message': 'hello'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Hello world.'})

    def test_without_a_message_still_returns_valid_json(self):
        response = self._post({})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Hello world.'})
