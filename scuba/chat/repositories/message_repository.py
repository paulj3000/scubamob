"""
MessageRepository interface (docs/chat_dynamo.md §15), an in-memory fake
for local development and unit tests (§58), and the real boto3-backed
DynamoDB implementation (Phase 2).
"""
import base64
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError
from django.utils import timezone

from scuba.chat.domain import Message, conversation_partition_key, message_sort_key
from scuba.chat.exceptions import MessageNotFoundError, RepositoryUnavailableError
from scuba.chat.infrastructure.dynamodb import get_client, get_table


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


_CLIENT_MESSAGE_SORT_KEY_PREFIX = 'CLIENT_MSG#'
MESSAGE_ID_INDEX = 'MessageIdIndex'
_type_serializer = TypeSerializer()


def _client_message_sort_key(client_message_id: str) -> str:
    return f"{_CLIENT_MESSAGE_SORT_KEY_PREFIX}{client_message_id}"


def _serialize_item(item: dict) -> dict:
    """ Raw AttributeValue map -- only needed for the low-level transact_write_items call. """
    return {key: _type_serializer.serialize(value) for key, value in item.items()}


def _message_to_item(message: Message) -> dict:
    item = {
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
    return {key: value for key, value in item.items() if value is not None}


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


def _encode_cursor(last_evaluated_key: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(last_evaluated_key).encode()).decode()


def _decode_cursor(cursor: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())


class DynamoDBMessageRepository(MessageRepository):
    """
    Real implementation (Phase 2). All DynamoDB-specific detail lives here;
    callers only ever see scuba.chat.domain.Message objects (§15).

    Expected table schema -- provisioned via infrastructure-as-code (§37),
    never created by this code:

        Table: PK (partition key, string), SK (sort key, string)
        GSI "MessageIdIndex": message_id (partition key, string),
            ProjectionType=ALL

    The GSI exists because get_message/update_message/soft_delete_message
    are keyed by message_id alone -- SK also folds in created_at (§6), which
    callers don't have, so a direct get_item on the base table isn't
    possible for those operations. Only message items carry a message_id
    attribute; the idempotency claim item below deliberately does not, so
    it never shows up in this GSI (sparse index).

    Idempotency (§18): a create_message with a client_message_id writes the
    message item and a second "claim" item (PK=conversation, SK=CLIENT_MSG#
    <client_message_id>, target_message_id=<the real message id>) in one
    TransactWriteItems call, both conditioned on attribute_not_exists(PK).
    A concurrent retry loses the transaction, not silently double-writes --
    the caller gets the message the winning request created.
    """

    def __init__(self, table_name: Optional[str] = None):
        self._table_name = table_name

    @property
    def _table(self):
        return get_table(self._table_name) if self._table_name else get_table()

    def create_message(self, message: Message) -> Message:
        item = _message_to_item(message)

        if not message.client_message_id:
            self._table.put_item(Item=item)
            return message

        claim_item = {
            'PK': conversation_partition_key(message.conversation_id),
            'SK': _client_message_sort_key(message.client_message_id),
            'target_message_id': message.message_id,
        }
        try:
            get_client().transact_write_items(TransactItems=[
                {'Put': {
                    'TableName': self._table.name,
                    'Item': _serialize_item(item),
                    'ConditionExpression': 'attribute_not_exists(PK)',
                }},
                {'Put': {
                    'TableName': self._table.name,
                    'Item': _serialize_item(claim_item),
                    'ConditionExpression': 'attribute_not_exists(PK)',
                }},
            ])
            return message
        except ClientError as error:
            if error.response.get('Error', {}).get('Code') != 'TransactionCanceledException':
                raise RepositoryUnavailableError(str(error)) from error
            existing = self.get_message_by_client_id(
                message.conversation_id, message.client_message_id)
            if existing is not None:
                return existing
            raise

    def get_message(self, conversation_id: str, message_id: str) -> Optional[Message]:
        item = self._find_item_by_message_id(conversation_id, message_id)
        return _item_to_message(item) if item is not None else None

    def get_message_by_client_id(
        self, conversation_id: str, client_message_id: str
    ) -> Optional[Message]:
        response = self._table.get_item(Key={
            'PK': conversation_partition_key(conversation_id),
            'SK': _client_message_sort_key(client_message_id),
        })
        claim = response.get('Item')
        if claim is None:
            return None
        return self.get_message(conversation_id, claim['target_message_id'])

    def list_messages(
        self, conversation_id: str, limit: int = 50, cursor: Optional[str] = None
    ) -> tuple[list[Message], Optional[str]]:
        query_kwargs = {
            'KeyConditionExpression': (
                Key('PK').eq(conversation_partition_key(conversation_id))
                & Key('SK').begins_with('MESSAGE#')
            ),
            'Limit': limit,
            'ScanIndexForward': True,
        }
        if cursor:
            query_kwargs['ExclusiveStartKey'] = _decode_cursor(cursor)

        response = self._table.query(**query_kwargs)
        messages = [_item_to_message(item) for item in response.get('Items', [])]
        next_cursor = (
            _encode_cursor(response['LastEvaluatedKey'])
            if 'LastEvaluatedKey' in response else None
        )
        return messages, next_cursor

    def update_message(self, conversation_id: str, message_id: str, *, body: str) -> Message:
        key = self._find_primary_key(conversation_id, message_id)
        if key is None:
            raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")

        self._table.update_item(
            Key=key,
            UpdateExpression='SET body = :body, edited_at = :edited_at',
            ExpressionAttributeValues={':body': body, ':edited_at': timezone.now().isoformat()},
        )
        return self.get_message(conversation_id, message_id)

    def soft_delete_message(self, conversation_id: str, message_id: str) -> Message:
        key = self._find_primary_key(conversation_id, message_id)
        if key is None:
            raise MessageNotFoundError(f"no message {message_id} in conversation {conversation_id}")

        self._table.update_item(
            Key=key,
            UpdateExpression='SET deleted_at = :deleted_at',
            ExpressionAttributeValues={':deleted_at': timezone.now().isoformat()},
        )
        return self.get_message(conversation_id, message_id)

    def _find_item_by_message_id(self, conversation_id: str, message_id: str) -> Optional[dict]:
        response = self._table.query(
            IndexName=MESSAGE_ID_INDEX,
            KeyConditionExpression=Key('message_id').eq(message_id),
            Limit=1,
        )
        items = response.get('Items', [])
        if not items or items[0].get('conversation_id') != conversation_id:
            return None
        return items[0]

    def _find_primary_key(self, conversation_id: str, message_id: str) -> Optional[dict]:
        item = self._find_item_by_message_id(conversation_id, message_id)
        return {'PK': item['PK'], 'SK': item['SK']} if item is not None else None
