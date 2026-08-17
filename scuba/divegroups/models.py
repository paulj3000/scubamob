from django.db import models

from scuba.accounts.models import User


class Group(models.Model):
    user = models.ForeignKey(User, related_name='group_owner', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True)
    privacy = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'divegroups'
        unique_together = (('user', 'title'), )

    def is_user_admin(self, user):
        return self.groups.filter(user=user, isadmin=True).exists()


class GroupUser(models.Model):
    group = models.ForeignKey(Group, related_name='groups', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='group_user', on_delete=models.CASCADE)
    isadmin = models.BooleanField(default=False)    # is this user an admin of the group
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
