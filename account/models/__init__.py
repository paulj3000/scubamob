import datetime
import time
import random
import uuid
import string

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


from account.models.manager import NotificationManager

from utils.core.models import Timestamped
#from utils.db import models

class Account(models.Model):
    user = models.ForeignKey(User, related_name='account' )
    guid = models.CharField(max_length=40)
    can_add_divesites = models.BooleanField(default=False)
    reputation = models.IntegerField(max_length=6, default=0)

    apikey = models.CharField(max_length=32)
    secret = models.CharField(max_length=16)

    is_private  = models.BooleanField(default=False)

    mongo_obj    = None

    def get_mongo(self):
        if not self.mongo_obj:
            self.mongo_obj = AccountMongo(user_id=self.id)

        return self.mongo_obj

    class Meta:
        db_table = 'account'

    def get_active_friend_requests(self): 
        ## let's get our user object
        user    = self.user                
      
        ## check for requests which have the user's email, but do not have a friend (user) id
        ## associated to it.  We will update the friend id with the current user
        UserFriendRequest.objects.filter(friend__id=0, email=user.email).update(friend=user)   
       
        ### now, let's actually run the query and return
        user.friend_requested.filter(active=1).sort('first_name')

    def init_guid(self):
        retval = 0
        for i in list(str(datetime.date.today().year)):
            retval += int(i)

        retval  = "%i-%s" % (retval, str(uuid.uuid1()).replace('-',''))

        ### ok, we have a new account id.  return it
        return retval
    
    def save(self, *args, **kwargs):
        if not self.apikey and not self.secret:
            self.apikey = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(24))
            self.secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        super(Account, self).save(*args, **kwargs)


class Friendship(models.Model):
    friend1 = models.ForeignKey(User, related_name='friend_friend1')
    friend2 = models.ForeignKey(User, related_name='friend_friend2')
    blocked = models.BooleanField(default=False)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'friendship'
        unique_together = (('friend1', 'friend2'), )

class UserFriend(models.Model):
    user = models.ForeignKey(User, related_name='friend_user' )
    friend = models.ForeignKey(User, related_name='friend_friend')
    hide = models.BooleanField(default=False)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'user_friend'
        unique_together = (('user', 'friend'), )

class UserFriendBlocked(models.Model):
    user = models.ForeignKey(User, null=True, related_name='blocked_user')
    friend = models.ForeignKey(User, related_name='blocked_friend')
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'user_friend_blocked'
        unique_together = (('user', 'friend'), )


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

class UserDiveSiteBuddyFinder(models.Model):
    user = models.ForeignKey(User, related_name='buddyfinder')
    divesite_id = models.CharField(max_length=100, null=True)
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        db_table = 'user_divesite_buddy_finder'
        unique_together = (('user', 'divesite_id'), )

##### this is for notifications
class Notification(models.Model):
    NOTIFICATION_TYPE = (
        (1, 'FRIEND_REQUEST'),
    )
    user = models.ForeignKey(User, related_name='notifications' )
    notification_type    = models.PositiveSmallIntegerField(max_length=3, choices=NOTIFICATION_TYPE)
    notification_id    = models.PositiveIntegerField(max_length=10)
    active = models.BooleanField(default=True)

    #### get our new manager
    objects = NotificationManager()

    class Meta:
        db_table = 'notification'


### define a signal, make sure we have an account set up for the user
def create_account(sender, **kw):
    user = kw["instance"]
    
    ### make sure we have an acccount
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

