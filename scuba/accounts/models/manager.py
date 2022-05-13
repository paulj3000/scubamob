from django.db import models

class NotificationManager(models.Manager):
    def add_friend_request_notification(self, user, request_id):
        from account.models import Notification
        Notification.objects.create(user=user, notification_type=1, notification_id=request_id)
