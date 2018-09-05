from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.utils.translation import ugettext_lazy as _

from account.models import Notification

# Create your models here.

class Friendship(models.Model):
    friend1 = models.ForeignKey(User, related_name='friend_friend1')
    friend2 = models.ForeignKey(User, related_name='friend_friend2')
    blocked = models.BooleanField(default=False)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'friendship'
        unique_together = (('friend1', 'friend2'), )

class UserFriendRequestManager(models.Manager):
    #@transaction.commit_on_success
    def update_friend_request_active(self, user):
        ## now, create the new blacklist version
        UserFriendRequest.objects.filter(friend=user, active=True).update(active=False)

class UserFriendRequest(models.Model):
    user = models.ForeignKey(User, null=True, related_name='friend_requests')
    email = models.CharField(max_length=100, null=True)
    active  = models.BooleanField(default=True)
    friend = models.ForeignKey(User, related_name='friend_requested')
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    # instantiate the new manager
    objects = UserFriendRequestManager()

    class Meta:
        db_table = 'user_friend_request'
        unique_together = (('user', 'friend'), ('user','email'), )

    # this is not needed if small_image is created at set_image
    def save(self, *args, **kwargs):
        super(UserFriendRequest, self).save(*args, **kwargs)
        Notification.objects.add_friend_request_notification(self.user, self.id)


class UserFriendBlocked(models.Model):
    user = models.ForeignKey(User, null=True, related_name='blocked_user')
    friend = models.ForeignKey(User, related_name='blocked_friend')
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'user_friend_blocked'
        unique_together = (('user', 'friend'), )


class Group(models.Model):
    user    = models.ForeignKey(User, related_name='group_owner')
    title = models.CharField(max_length=100, unique=True)
    description         =  models.CharField(max_length=255, null=True)
    privacy             = models.IntegerField(max_length=1, default=0)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'group'

    def is_user_admin(self, user):
        return True if self.groups.filter(user=user).count() else False

class GroupUser(models.Model):
    group = models.ForeignKey(Group, related_name='groups')
    user    = models.ForeignKey(User, related_name='group_user')
    isadmin  = models.BooleanField(default=True)    ### is this user an admin of the site
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'group_user'
        unique_together = (('group', 'user'), )

class GroupUserJoinRequest(models.Model):
    group = models.ForeignKey(Group)
    user    = models.ForeignKey(User)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'group_user_join_request'
        unique_together = (('group', 'user'), )
