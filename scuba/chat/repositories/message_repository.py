"""
MessageRepository interface (docs/chat_dynamo.md §15), an in-memory fake
for local development and tests (§58: "Production may use DynamoDB, but
development must remain easy"; Phase 0 task: "Add DynamoDB local/test
strategy"), and the real boto3-backed implementation (Phase 2).

CLAUDE.md requires tests never depend on a live external service, so
DynamoDBMessageRepository's own tests mock boto3 directly (matching
scuba.libs.aws.s3's existing test convention) rather than hitting
DynamoDB Local -- chat.services' tests use the in-memory fake instead.
"""
import base64
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from boto3.dynamodb.conditions import Attr, Key
from django.utils import timezone

from scuba.chat.domain import Message, conversation_partition_key, message_sort_key
from scuba.chat.exceptions import MessageNotFoundError
from scuba.chat.infrastructure.dynamodb import get_table


class MessageRepository(ABC):
    """ All DynamoDB-specific detail must live behind this interface (§15). """

    @abstractmethod
    def create_message(self, message: Message) -> Message:
        """ Persist a new message. Idempotent on message.client_message_id (§18). """

    @abstractmethod
    def get_message(self, conversation_id: str, message_id: str) -> Optional[Message]:
        ...

    @abstractmethod
    def get_message_by_client_id(
        self, conversation_id: str, client_message_id: str
    ) -> Optional[Message]:
        """ Idempotency lookup (§18): a retried send must not create a duplicate. """

    @abstractmethod
    def list_messages(
        self, conversation_id: str, limit: int = 50, cursor: Optional[str] = None
    ) -> tuple[list[Message], Optional[str]]:
        """
        Returns (messages, next_cursor), chronologically ordered.

        Cursor-based, never offset-based (§10) -- DynamoDB Query doesn't
        support offsets.
        """

    @abstractmethod
    def update_message(self, conversation_id: str, message_id: str, *, body: str) -> Message:
        ...

    @abstractmethod
    def soft_delete_message(self, conversation_id: str, message_id: str) -> Message:
        """ Sets deleted_at rather than removing the item (§40). """


class InMemoryMessageRepository(MessageRepository):
    """ Dict-backed fake. No network calls -- safe for unit tests. """

    def __init__(self):
        self._by_conversation: dict[str, dict[str, Message]] = {}
        self._by_client_id: dict[tuple[str, str], str] = {}

    def create_message(self, message: Message) -> Message:
        if message.client_message_id:
            existing = self.get_message_by_client_id(
                message.conversation_id, message.client_message_id)
            if existing is not None:
                return existing

        conversation = self._by_conversation.setdefault(message.conversation_id, {})
        conversation[message.message_id] = message

        if message.client_message_id:
            key = (message.conversation_id, message.client_message_id)
            self._by_client_id[key] = message.message_id

        return message

    def get_message(self, conversation_id: str, message_id: str) -> Optional[Message]:
        return self._by_conversation.get(conversation_id, {}).get(message_id)

    def get_message_by_client_id(
        self, conversation_id: str, client_message_id: str
    ) -> Optional[Message]:
        message_id = self._by_client_id.get((conversation_id, client_message_id))
        if message_id is None:
            return None
        return self.get_message(conversation_id, message_id)

    def list_messages(
        self, conversation_id: str, limit: int = 50, cursor: Optional[str] = None
    ) -> tuple[list[Message], Optional[str]]:
        messages = sorted(
            self._by_conversation.get(conversation_id, {}).values(),
            key=lambda message: message.created_at,
        )
        start = int(cursor) if cursor else 0
        page = messages[start:start + limit]
        next_cursor = str(start + limit) if start + limit < len(messages) else None
        return page, next_cursor

    def update_message(self, conversation_id: str, message_id: str, *, body: str) -> Message:
        message = self.get_message(conversation_id, message_id)
        if message is None:
            raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")
        message.body = body
        message.edited_at = timezone.now()
        return message

    def soft_delete_message(self, conversation_id: str, message_id: str) -> Message:
        message = self.get_message(conversation_id, message_id)
        if message is None:
            raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")
        message.deleted_at = timezone.now()
        return message


def _encode_cursor(last_evaluated_key: dict) -> str:
    """ Opaque cursor over DynamoDB's own LastEvaluatedKey (§10) -- never an offset. """
    return base64.urlsafe_b64encode(json.dumps(last_evaluated_key).encode()).decode()


def _decode_cursor(cursor: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())


def _message_to_item(message: Message) -> dict:
    return {
        'PK': conversation_partition_key(message.conversation_id),
        'SK': message_sort_key(message.created_at, message.message_id),
        'message_id': message.message_id,
        'conversation_id': message.conversation_id,
        'sender_id': message.sender_id,
        'message_type': message.message_type,
        'body': message.body,
        'created_at': message.created_at.isoformat(),
        'client_message_id': message.client_message_id,
        'edited_at': message.edited_at.isoformat() if message.edited_at else None,
        'deleted_at': message.deleted_at.isoformat() if message.deleted_at else None,
        'reply_to_message_id': message.reply_to_message_id,
        'entity_type': message.entity_type,
        'entity_id': message.entity_id,
    }


def _item_to_message(item: dict) -> Message:
    return Message(
        message_id=item['message_id'],
        conversation_id=item['conversation_id'],
        sender_id=item['sender_id'],
        message_type=item['message_type'],
        body=item['body'],
        created_at=datetime.fromisoformat(item['created_at']),
        client_message_id=item.get('client_message_id'),
        edited_at=datetime.fromisoformat(item['edited_at']) if item.get('edited_at') else None,
        deleted_at=datetime.fromisoformat(item['deleted_at']) if item.get('deleted_at') else None,
        reply_to_message_id=item.get('reply_to_message_id'),
        entity_type=item.get('entity_type'),
        entity_id=item.get('entity_id'),
    )


class DynamoDBMessageRepository(MessageRepository):
    """
    Real implementation (§15), backed by the single-table design in §6/§7:
    PK = CONVERSATION#<conversation_id>, SK = MESSAGE#<created_at>#<message_id>.

    get_message/update_message/soft_delete_message and the client-message-id
    idempotency lookup all take a message id or client id without the
    timestamp half of the sort key, so none of them can do a plain GetItem
    -- each does a partition Query (already the primary access pattern,
    §6) filtered down to the one matching item. This is intentionally not
    a table Scan and is bounded by one conversation's message count, but
    per §8's own rule against speculative indexes, no GSI was added for
    these secondary lookups; revisit if a conversation's message volume
    ever makes the filtered Query too expensive.
    """

    def _table(self):
        return get_table()

    def _find_item(self, conversation_id: str, message_id: str) -> Optional[dict]:
        response = self._table().query(
            KeyConditionExpression=Key('PK').eq(conversation_partition_key(conversation_id)),
            FilterExpression=Attr('message_id').eq(message_id),
        )
        items = response.get('Items', [])
        return items[0] if items else None

    def create_message(self, message: Message) -> Message:
        if message.client_message_id:
            existing = self.get_message_by_client_id(
                message.conversation_id, message.client_message_id)
            if existing is not None:
                return existing

        self._table().put_item(Item=_message_to_item(message))
        return message

    def get_message(self, conversation_id: str, message_id: str) -> Optional[Message]:
        item = self._find_item(conversation_id, message_id)
        return _item_to_message(item) if item else None

    def get_message_by_client_id(
        self, conversation_id: str, client_message_id: str
    ) -> Optional[Message]:
        response = self._table().query(
            KeyConditionExpression=Key('PK').eq(conversation_partition_key(conversation_id)),
            FilterExpression=Attr('client_message_id').eq(client_message_id),
        )
        items = response.get('Items', [])
        return _item_to_message(items[0]) if items else None

    def list_messages(
        self, conversation_id: str, limit: int = 50, cursor: Optional[str] = None
    ) -> tuple[list[Message], Optional[str]]:
        query_kwargs = {
            'KeyConditionExpression': Key('PK').eq(conversation_partition_key(conversation_id)),
            'Limit': limit,
            'ScanIndexForward': True,
        }
        if cursor:
            query_kwargs['ExclusiveStartKey'] = _decode_cursor(cursor)

        response = self._table().query(**query_kwargs)
        messages = [_item_to_message(item) for item in response.get('Items', [])]
        next_cursor = (
            _encode_cursor(response['LastEvaluatedKey'])
            if 'LastEvaluatedKey' in response else None
        )
        return messages, next_cursor

    def update_message(self, conversation_id: str, message_id: str, *, body: str) -> Message:
        item = self._find_item(conversation_id, message_id)
        if item is None:
            raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")

        edited_at = timezone.now()
        self._table().update_item(
            Key={'PK': item['PK'], 'SK': item['SK']},
            UpdateExpression='SET body = :body, edited_at = :edited_at',
            ExpressionAttributeValues={':body': body, ':edited_at': edited_at.isoformat()},
        )

        message = _item_to_message(item)
        message.body = body
        message.edited_at = edited_at
        return message

    def soft_delete_message(self, conversation_id: str, message_id: str) -> Message:
        item = self._find_item(conversation_id, message_id)
        if item is None:
            raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")

        deleted_at = timezone.now()
        self._table().update_item(
            Key={'PK': item['PK'], 'SK': item['SK']},
            UpdateExpression='SET deleted_at = :deleted_at',
            ExpressionAttributeValues={':deleted_at': deleted_at.isoformat()},
        )

        message = _item_to_message(item)
        message.deleted_at = deleted_at
        return message
