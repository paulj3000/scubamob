import datetime
import time
import random
import uuid
import string

from django.contrib.auth.models import (
    AbstractUser, UserManager
)

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

from rest_framework.authtoken.models import Token

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.settings import PROFILE_BLANK_URL


class User(AbstractUser, UUIDModel):
    aws_id = models.CharField(max_length=10, blank=True)
    last_login_date = models.DateTimeField(null=True)
    can_add_divesites = models.BooleanField(default=False)
    reputation = models.PositiveSmallIntegerField(default=0)
    is_private = models.BooleanField(default=False)

    class Meta:
        db_table = 'user'
        ordering = ['-date_joined']

    @property
    def get_id_str(self):
        return str(self.id).replace('-', '')

    def __str__(self):
        return self.get_full_name()

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

    # -----------------------------------------------------------------------------
    # start Friendship stuff
    # -----------------------------------------------------------------------------
    def get_active_friend_requests(self):
        # let's get our user object
        user = self.user

        # check for requests which have the user's email,
        # but do not have a friend (user) id associated to it.
        # We will update the friend id with the current user
        UserFriendRequest.objects.filter(
            friend__id=0, email=user.email
        ).update(friend=user)

        # now, let's actually run the query and return
        user.friend_requested.filter(active=1).sort('first_name')

    def get_friend(self, friend):
        # get all of the current friends
        return User.objects.filter(
                Q(friend_friend1__friend1=friend) |
                Q(friend_friend2__friend2=friend)).first()

    def get_friend_count(self):
        # get all of the current friends
        return self.friends.all().count()

    def get_all_friends(self):
        # return all of the friends that is not us!
        Friendship.objects.filter(Q(friend2=self) | Q(friend1=self)).values('friend1', 'friend2')

    def block_friend(self, friend):
        # get all of the current friends
        UserFriendBlocked.objects.create(user=self, friend=friend)

        # now, let's delete all friend requests...
        UserFriendRequest.objects.filter(Q(user=friend, friend=self) |
                                         Q(user=self, friend=friend)).delete()

    def get_blocked_friends(self):
        # get all of the current friends
        return self.blocked_user.order_by('friend__first_name')

    def is_blocked(self, friend):
        # check if the user is blocking for the friend.
        return UserFriendBlocked.objects.filter(Q(user=friend, friend=self) |
                                                Q(user=self, friend=friend)).count()

    # -----------------------------------------------------------------------------
    # start profile image stuff
    # -----------------------------------------------------------------------------

    def get_profile_image(self):
        ''' return a profile image. make sure they have a user profile object
        first. Later, if no profile image exists, return a default avatar '''

        if hasattr(self, 'userprofileimage'):
            return self.userprofileimage.get_profile_image()

        # No profile image. just return a default
        return static(PROFILE_BLANK_URL)

    def upload_profile_image_as_string(self, uploaded_image_string):
        ''' upload a profile image to S3 when the uploaded image is sent
        over as a string
        Params:
            uploaded_image_string: a string representation of a profile image
        '''
        # generate the file name the
        img_length = 5 # the sub key length
        sub_name = StringUtils.generate_random_number(img_length)
        base_name = "profiles/%s/%s_%d.png" % (self.get_aws_id(), sub_name, int(time.time()))

        #if re.search(r'^data:image\/(jpg|png);base64', uploaded_image_string, re.DOTALL):
        result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", uploaded_image_string)

        profile_image = None
        if result:
            ext = result.groupdict().get("ext")
            data = result.groupdict().get("data")

            img = base64.urlsafe_b64decode(data)
            User.upload_image(base_name, 'image/%s' % ext, img)

            # does the user have a prfofile image? if so, replace it
            if hasattr(self, 'userprofileimage'):
                profile_image = getattr(self, 'userprofileimage')
                profile_image.image = base_name
                profile_image.save()
            else:
                profile_image = UserProfileImage.objects.create(user=self, image=base_name)

        # return the new profile image
        return profile_image


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    is_blocked = models.BooleanField(default=False)
    aws_id = models.CharField(max_length=10, blank=True)
    guid = models.CharField(max_length=40)
    can_add_divesites = models.BooleanField(default=False)
    reputation = models.PositiveSmallIntegerField(default=0)
    is_private = models.BooleanField(default=False)

    apikey = models.CharField(max_length=32)
    secret = models.CharField(max_length=16)

    mongo_obj = None

    def get_mongo(self):
        if not self.mongo_obj:
            self.mongo_obj = AccountMongo(user_id=self.id)

        return self.mongo_obj

    class Meta:
        db_table = 'account'

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
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'friendship'
        unique_together = (('friend1', 'friend2'), )


class UserFriend(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, on_delete=models.CASCADE)
    hide = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_friend'
        unique_together = (('user', 'friend'), )


class UserFriendBlocked(models.Model):
    user = models.ForeignKey(User, null=True, related_name='blocked_user', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='blocked_friend', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

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
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # instantiate the new manager
    objects = UserFriendRequestManager()

    class Meta:
        db_table = 'user_friend_request'
        unique_together = (('user', 'friend'), ('user','email'), )

class UserDiveSiteBuddyFinder(models.Model):
    user = models.ForeignKey(User, related_name='buddyfinder', on_delete=models.CASCADE)
    divesite_id = models.CharField(max_length=100, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'user_divesite_buddy_finder'
        unique_together = (('user', 'divesite_id'), )


class UserLocation(UUIDModel):
    """ UserLocation

    Keep a representation of the user's profile image
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=16)
    city = models.CharField(max_length=128)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_location'


class UserProfileImage(UUIDModel):
    """ UserProfileImage

    Keep a representation of the user's profile image
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.CharField(max_length=128)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_profile_image'

    def __str__(self):
        """ return a string representation of the model """
        return self.user.get_full_name()

    @property
    def image_cleaned(self):
        return self.image.replace('programs/', '')

    def get_profile_image(self):
        """ get_profile_image

        sanitize the profile image. This will return the full url path
        of the profile image, sans the 'profiles/' prefix
        """
        return f"{CLOUDFRONT}{self.image_cleaned}"
