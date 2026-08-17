"""
AttachmentRepository interface (docs/chat_dynamo.md §4.3, §30, Phase 11),
an in-memory fake for local development and unit tests (§58), and the real
DynamoDB-backed implementation.

Binary content lives in S3; DynamoDB (or the message item itself) stores
only the reference (§31, §5 "DynamoDB should contain only attachment
metadata and object references."). AttachmentRepository owns that
metadata, mirroring MessageRepository's split (§15). AttachmentStorage is
the sibling abstraction for the S3 side: uploading the raw bytes and
minting a signed URL to read them back (§30: "Use signed URLs when
private content is retrieved.").
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from boto3.dynamodb.conditions import Key

from scuba.chat.domain import Attachment, attachment_sort_key, conversation_partition_key
from scuba.chat.infrastructure import s3 as s3_infra
from scuba.chat.infrastructure.dynamodb import get_table

ATTACHMENT_ID_INDEX = 'AttachmentIdIndex'


class AttachmentRepository(ABC):
    @abstractmethod
    def create_attachment(self, attachment: Attachment) -> Attachment:
        """ Persist attachment metadata. The file itself is already in S3 by this point. """

    @abstractmethod
    def get_attachment(self, conversation_id: str, attachment_id: str) -> Optional[Attachment]:
        ...

    @abstractmethod
    def list_attachments_for_message(self, conversation_id: str, message_id: str) -> list[Attachment]:
        ...


class InMemoryAttachmentRepository(AttachmentRepository):
    """ Dict-backed fake. No network calls -- safe for unit tests. """

    def __init__(self):
        self._by_conversation: dict[str, dict[str, Attachment]] = {}

    def create_attachment(self, attachment: Attachment) -> Attachment:
        conversation = self._by_conversation.setdefault(attachment.conversation_id, {})
        conversation[attachment.attachment_id] = attachment
        return attachment

    def get_attachment(self, conversation_id: str, attachment_id: str) -> Optional[Attachment]:
        return self._by_conversation.get(conversation_id, {}).get(attachment_id)

    def list_attachments_for_message(self, conversation_id: str, message_id: str) -> list[Attachment]:
        attachments = self._by_conversation.get(conversation_id, {}).values()
        return sorted(
            (attachment for attachment in attachments if attachment.message_id == message_id),
            key=lambda attachment: attachment.created_at)


def _attachment_to_item(attachment: Attachment) -> dict:
    item = {
        'PK': conversation_partition_key(attachment.conversation_id),
        'SK': attachment_sort_key(attachment.message_id, attachment.attachment_id),
        'attachment_id': attachment.attachment_id,
        'conversation_id': attachment.conversation_id,
        'message_id': attachment.message_id,
        'attachment_type': attachment.attachment_type,
        's3_key': attachment.s3_key,
        'content_type': attachment.content_type,
        'size': attachment.size,
        'created_at': attachment.created_at.isoformat(),
        'original_filename': attachment.original_filename,
    }
    return {key: value for key, value in item.items() if value is not None}


def _item_to_attachment(item: dict) -> Attachment:
    return Attachment(
        attachment_id=item['attachment_id'],
        conversation_id=item['conversation_id'],
        message_id=item['message_id'],
        attachment_type=item['attachment_type'],
        s3_key=item['s3_key'],
        content_type=item['content_type'],
        size=int(item['size']),
        created_at=datetime.fromisoformat(item['created_at']),
        original_filename=item.get('original_filename'),
    )


class DynamoDBAttachmentRepository(AttachmentRepository):
    """
    Real implementation (Phase 11). Shares the chat messages table (§5
    groups "Rich-message payload references" alongside Message under
    DynamoDB ownership) -- attachment items live in the same conversation
    partition as their message, distinguished by the ATTACHMENT# SK prefix
    (mirrors MESSAGE#, §6).

    Expected table schema addition, provisioned via infrastructure-as-code
    (§37), never created by this code:

        GSI "AttachmentIdIndex": attachment_id (partition key, string),
            ProjectionType=ALL

    Needed because get_attachment is keyed by attachment_id alone, same
    reasoning as MessageRepository's MessageIdIndex (message_repository.py).
    """

    def __init__(self, table_name: Optional[str] = None):
        self._table_name = table_name

    @property
    def _table(self):
        return get_table(self._table_name) if self._table_name else get_table()

    def create_attachment(self, attachment: Attachment) -> Attachment:
        self._table.put_item(Item=_attachment_to_item(attachment))
        return attachment

    def get_attachment(self, conversation_id: str, attachment_id: str) -> Optional[Attachment]:
        response = self._table.query(
            IndexName=ATTACHMENT_ID_INDEX,
            KeyConditionExpression=Key('attachment_id').eq(attachment_id),
            Limit=1,
        )
        items = response.get('Items', [])
        if not items or items[0].get('conversation_id') != conversation_id:
            return None
        return _item_to_attachment(items[0])

    def list_attachments_for_message(self, conversation_id: str, message_id: str) -> list[Attachment]:
        response = self._table.query(
            KeyConditionExpression=(
                Key('PK').eq(conversation_partition_key(conversation_id))
                & Key('SK').begins_with(f"ATTACHMENT#{message_id}#")
            ),
        )
        return [_item_to_attachment(item) for item in response.get('Items', [])]


class AttachmentStorage(ABC):
    """ The S3 side of an attachment: raw bytes in, a signed read URL out. """

    @abstractmethod
    def upload(self, key: str, fileobj, *, content_type: str) -> None:
        ...

    @abstractmethod
    def get_download_url(self, key: str, *, expires_in: int = 300) -> str:
        """ A time-limited signed URL (§30: private content must never use a bare public URL). """


class InMemoryAttachmentStorage(AttachmentStorage):
    """ Dict-backed fake. No network calls -- safe for unit tests. """

    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def upload(self, key: str, fileobj, *, content_type: str) -> None:
        data = fileobj.read() if hasattr(fileobj, 'read') else fileobj
        self.objects[key] = data

    def get_download_url(self, key: str, *, expires_in: int = 300) -> str:
        return f"memory://{key}?expires_in={expires_in}"


class S3AttachmentStorage(AttachmentStorage):
    """ Real implementation (Phase 11), backed by CHAT_ATTACHMENT_BUCKET. """

    def upload(self, key: str, fileobj, *, content_type: str) -> None:
        body = fileobj.read() if hasattr(fileobj, 'read') else fileobj
        s3_infra.get_client().put_object(
            Bucket=s3_infra.get_bucket_name(), Key=key, Body=body, ContentType=content_type)

    def get_download_url(self, key: str, *, expires_in: int = 300) -> str:
        return s3_infra.get_client().generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_infra.get_bucket_name(), 'Key': key},
            ExpiresIn=expires_in,
        )
