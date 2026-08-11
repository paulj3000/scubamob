"""
AttachmentRepository interface (docs/chat_dynamo.md §4.3, §31).

Binary content lives in S3; DynamoDB (or the message item itself) stores
only the reference (§31, §5 "DynamoDB should contain only attachment
metadata and object references."). The real implementation is Phase 11.
"""
from abc import ABC, abstractmethod


class AttachmentRepository(ABC):
    @abstractmethod
    def create_attachment(
        self, conversation_id: str, message_id: str, *, s3_key: str, content_type: str
    ) -> dict:
        ...

    @abstractmethod
    def get_attachment(self, conversation_id: str, attachment_id: str) -> dict:
        ...
