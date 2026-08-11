from django.test import SimpleTestCase

from scuba.chat.events import ChatEvent, MessageEventType


class TestChatEvent(SimpleTestCase):
    def test_as_dict_matches_the_documented_envelope(self):
        event = ChatEvent(
            event=MessageEventType.MESSAGE_CREATED,
            conversation_id='12345',
            payload={'message': {'body': 'hi'}},
        )

        self.assertEqual(event.as_dict(), {
            'event': 'message.created',
            'conversation_id': '12345',
            'message': {'body': 'hi'},
        })

    def test_payload_defaults_to_empty(self):
        event = ChatEvent(event=MessageEventType.TYPING_STARTED, conversation_id='12345')

        self.assertEqual(event.as_dict(), {
            'event': 'typing.started',
            'conversation_id': '12345',
        })
