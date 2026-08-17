"""
NotificationRepository interface (docs/chat_dynamo.md §4.3, §29, Phase 10)
and the Django-ORM-backed implementation.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from django.utils import timezone

from scuba.chat.models import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def create_notification(
        self, *, recipient_id: str, conversation_id: str, actor_id: str, message_id: str
    ) -> Any:
        ...

    @abstractmethod
    def list_notifications(
        self, recipient_id: str, *, unread_only: bool = False, limit: int = 50
    ) -> list[Any]:
        """ Newest first (§29's "Chris Kelly sent you a message" feed). """

    @abstractmethod
    def count_unread(self, recipient_id: str) -> int:
        ...

    @abstractmethod
    def mark_read(self, notification_id: str, recipient_id: str) -> Optional[Any]:
        """ Returns the updated notification, or None if it doesn't belong to recipient_id. """

    @abstractmethod
    def mark_all_read(self, recipient_id: str) -> None:
        ...


class DjangoNotificationRepository(NotificationRepository):
    """ Real implementation backed by the Phase 10 Notification model. """

    def create_notification(
        self, *, recipient_id: str, conversation_id: str, actor_id: str, message_id: str
    ) -> Notification:
        return Notification.objects.create(
            recipient_id=recipient_id, conversation_id=conversation_id,
            actor_id=actor_id, message_id=message_id,
        )

    def list_notifications(
        self, recipient_id: str, *, unread_only: bool = False, limit: int = 50
    ) -> list[Notification]:
        queryset = Notification.objects.filter(recipient_id=recipient_id)
        if unread_only:
            queryset = queryset.filter(read_at__isnull=True)
        return list(queryset[:limit])

    def count_unread(self, recipient_id: str) -> int:
        return Notification.objects.filter(recipient_id=recipient_id, read_at__isnull=True).count()

    def mark_read(self, notification_id: str, recipient_id: str) -> Optional[Notification]:
        updated = Notification.objects.filter(
            pk=notification_id, recipient_id=recipient_id, read_at__isnull=True,
        ).update(read_at=timezone.now())
        if not updated:
            return Notification.objects.filter(pk=notification_id, recipient_id=recipient_id).first()
        return Notification.objects.filter(pk=notification_id).first()

    def mark_all_read(self, recipient_id: str) -> None:
        Notification.objects.filter(
            recipient_id=recipient_id, read_at__isnull=True
        ).update(read_at=timezone.now())
