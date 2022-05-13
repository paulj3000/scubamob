import datetime
import time
import random
import uuid
import string


from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


from account.models.manager import NotificationManager

from utils.core.models import Timestamped
#from utils.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(email=email, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # return the new user
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    aws_id = models.CharField(max_length=10, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    guid = models.CharField(max_length=40)
    can_add_divesites = models.BooleanField(default=False)
    reputation = models.PositiveSmallIntegerField(default=0)

    apikey = models.CharField(max_length=32)
    secret = models.CharField(max_length=16)

    is_private = models.BooleanField(default=False)

    mongo_obj = None

    def get_mongo(self):
        if not self.mongo_obj:
            self.mongo_obj = AccountMongo(user_id=self.id)

        return self.mongo_obj


    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        db_table = 'user'

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def get_abbreviated_name(self):
        return "%s %s." % (self.first_name, self.last_name[0])

    def __unicode__(self):
        return self.get_full_name()

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    # -----------------------------------------------------------------------------
    # start API stuff (token based)
    # -----------------------------------------------------------------------------
    def get_api_token(self):
        """ get_api_token

        Get the API token for a particular user. If it does not exist, create id
        Returns: API Token
        """
        # send the email
        obj, _ = Token.objects.get_or_create(user=self)
        return obj.key

    def get_active_friend_requests(self):
        # let's get our user object
        user = self.user

        # check for requests which have the user's email, but do not have a friend (user) id
        # associated to it.  We will update the friend id with the current user
        UserFriendRequest.objects.filter(friend__id=0, email=user.email).update(friend=user)

        # now, let's actually run the query and return
        user.friend_requested.filter(active=1).sort('first_name')

    def init_guid(self):
        retval = 0
        for i in list(str(datetime.date.today().year)):
            retval += int(i)

        retval = "%i-%s" % (retval, str(uuid.uuid1()).replace('-',''))

        # ok, we have a new account id.  return it
        return retval

    def save(self, *args, **kwargs):
        if not self.apikey and not self.secret:
            self.apikey = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(24))
            self.secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        super().save(*args, **kwargs)


class Friendship(models.Model):
    friend1 = models.ForeignKey(User, related_name='friend_friend1', on_delete=models.CASCADE)
    friend2 = models.ForeignKey(User, related_name='friend_friend2', on_delete=models.CASCADE)
    blocked = models.BooleanField(default=False)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'friendship'
        unique_together = (('friend1', 'friend2'), )

class UserFriend(models.Model):
    user = models.ForeignKey(User, related_name='friend_user', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_friend', on_delete=models.CASCADE)
    hide = models.BooleanField(default=False)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'user_friend'
        unique_together = (('user', 'friend'), )

class UserFriendBlocked(models.Model):
    user = models.ForeignKey(User, null=True, related_name='blocked_user', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='blocked_friend', on_delete=models.CASCADE)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'user_friend_blocked'
        unique_together = (('user', 'friend'), )


class UserFriendRequestManager(models.Manager):
    #@transaction.commit_on_success
    def update_friend_request_active(self, user):
        # now, create the new blacklist version
        UserFriendRequest.objects.filter(friend=user, active=True).update(active=False)

class UserFriendRequest(models.Model):
    user = models.ForeignKey(User, null=True, related_name='friend_requests', on_delete=models.CASCADE)
    email = models.CharField(max_length=100, null=True)
    active = models.BooleanField(default=True)
    friend = models.ForeignKey(User, related_name='friend_requested', on_delete=models.CASCADE)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    # instantiate the new manager
    objects = UserFriendRequestManager()

    class Meta:
        db_table = 'user_friend_request'
        unique_together = (('user', 'friend'), ('user','email'), )

class UserDiveSiteBuddyFinder(models.Model):
    user = models.ForeignKey(User, related_name='buddyfinder', on_delete=models.CASCADE)
    divesite_id = models.CharField(max_length=100, null=True)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'user_divesite_buddy_finder'
        unique_together = (('user', 'divesite_id'), )

# this is for notifications
class Notification(models.Model):
    NOTIFICATION_TYPE = (
        (1, 'FRIEND_REQUEST'),
    )
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    notification_type = models.PositiveSmallIntegerField(choices=NOTIFICATION_TYPE)
    notification_id = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    # get our new manager
    objects = NotificationManager()

    class Meta:
        db_table = 'notification'


# define a signal, make sure we have an account set up for the user
def create_account(sender, **kw):
    user = kw["instance"]

    # make sure we have an acccount
    if kw["created"]:
        account = Account(user=user)
        account.save()
    else:
        try:
            user.account.get()
        except:
            account = Account(user=user)
            account.save()

post_save.connect(create_account, sender=User, dispatch_uid="users-accountcreation-signal")

