from django.db import models
from django.utils.translation import gettext_lazy as _

from scuba.accounts.models import User


class Group(models.Model):
    user = models.ForeignKey(User, related_name='group_owner', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, null=True)
    privacy = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'divegroups'

    def is_user_admin(self, user):
        return True if self.groups.filter(user=user).count() else False


class GroupUser(models.Model):
    group = models.ForeignKey(Group, related_name='groups', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='group_user', on_delete=models.CASCADE)
    isadmin = models.BooleanField(default=True)    # is this user an admin of the site
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'divegroup_user'
        unique_together = (('group', 'user'), )


class GroupUserJoinRequest(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'divegroup_user_join_request'
        unique_together = (('group', 'user'), )
