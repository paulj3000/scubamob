import datetime
import time
import random
import uuid
import string

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.templatetags.static import static
from django.core.exceptions import ValidationError

from bs4 import BeautifulSoup

from rest_framework.authtoken.models import Token

from scuba.accounts.settings import SETTINGS_KEYS, SETTINGS_VALUES
from scuba.libs.models.uuidmodel import UUIDModel
from scuba.libs.alerting import Alerting
from scuba.settings import PROFILE_BLANK_URL, AWS_CLOUDFRONT
from scuba.accounts.exceptions import InvalidEmailIdException, PrimaryEmailIdException, EmailInUseException, InvalidUserIdException, InvalidConfirmationCodeException
from scuba.accounts.settings import SETTINGS
from scuba.sitesettings.models import SystemSetting

from scuba.libs.mail import generate_email, send_mail
from scuba.content.models import EmailTemplate


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
        ''' override the create superuser function '''
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, UUIDModel):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    aws_id = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField()
    last_login_date = models.DateTimeField(null=True)
    can_add_divesites = models.BooleanField(default=False)
    reputation = models.PositiveSmallIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login_date = models.DateTimeField(null=True)

    objects = UserManager()

    class Meta:
        db_table = 'user'
        ordering = ['-date_joined']

    USERNAME_FIELD = 'email'

    @property
    def profile_image(self):
        return self.get_profile_image()

    @property
    def is_staff(self):
        return self.is_admin

    def get_full_name(self):
        """ get_full_name

        get the user's full name
        """
        return f"{self.first_name.strip()} {self.last_name.strip()}"

    def __str__(self):
        return self.get_full_name()

    @staticmethod
    def create_user(first_name, last_name, email, password, date_of_birth):
        return User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            date_of_birth=date_of_birth,
            confirmed=False)

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
    # start Buddy stuff
    # -----------------------------------------------------------------------------
    def get_active_buddy_requests(self):
        # let's get our user object
        user = self.user

        # check for requests which have the user's email,
        # but do not have a friend (user) id associated to it.
        # We will update the friend id with the current user
        UserBuddyRequest.objects.filter(
            friend__id=0, email=user.email
        ).update(friend=user)

        # now, let's actually run the query and return
        user.friend_requested.filter(active=1).sort('first_name')

    def get_friend(self, friend):
        # get all of the current buddies
        return User.objects.filter(
                Q(friend_friend1__friend1=friend) |
                Q(friend_friend2__friend2=friend)).first()

    def get_buddies_count(self):
        # get all of the current buddies
        return self.buddies.all().count()

    def get_all_buddies(self):
        # return all of the buddies that is not us!
        return self.buddies.all()

    def get_all_buddies_recent_activity(self):
        # return all of the buddies that is not us!
        return self.buddies.all().order_by('-user__activities__activity_date')

    def add_buddy(self, buddy):
        """ add_buddy

        add a buddy for the user
        """
        retval = self.buddies.create(buddy=buddy)
        buddy.buddies.create(buddy=self)
        return retval

    def get_buddy_status(self, userid):
        # return all of the buddies that is not us!
        try:
            user = User.objects.get(id=userid)

            data = self.buddy_requests.filter(buddy=user, is_active=True).first()
            if data:
                return {'state': 1, 'type': 'Requested', 'id': data.pk_as_str}

            data = self.buddies.filter(buddy=user).first()
            if data:
                return {'state': 2, 'type': 'Buddies', 'id': data.pk_as_str}

            data = self.buddy_requested.filter(buddy=self, is_active=True, is_deleted=False).first()
            if data:
                return {'state': 3, 'type': 'Was Requested', 'id': data.pk_as_str}

            return {'state': 0, 'type': 'Open'}
        except (ValidationError, User.DoesNotExist):
            raise InvalidUserIdException

    def get_all_buddy_requests(self):
        ''' get_all_buddy_requests

        Get all of the buddy requests
        '''
        return self.buddy_requests.all()

    def add_buddy_request(self, buddy):
        obj, created = self.buddy_requests.update_or_create(
            buddy=buddy,
            defaults={'is_active': True},
        )

        # return the object
        return obj

    def is_add_buddy_requested(self, buddy):
        return self.buddy_requests.filter(buddy=buddy, is_active=True).count()

    def cancel_buddy_request(self, buddy):
        return self.buddy_requests.filter(buddy=buddy, is_active=True).update(is_active=False)

    def block_buddy(self, buddy):
        # get all of the current buddies
        UserBlocked.objects.create(user=self, buddy=buddy, blocked_by=self)

        # now, let's delete all friend requests...
        UserBuddyRequest.objects.filter(Q(user=buddy, buddy=self) |
                                         Q(user=self, buddy=buddy)).delete()

    def get_blocked_buddies(self):
        # get all of the current buddies
        return self.blocked_user.order_by('friend__first_name')

    def is_blocked(self, buddy):
        # check if the user is blocking for the friend.
        return UserBlocked.objects.filter(Q(user=buddy, buddy=self) |
                                          Q(user=self, buddy=buddy)).count()

    # -----------------------------------------------------------------------------
    # start confirmation code stuff
    # -----------------------------------------------------------------------------
    def generate_confirmation_code(self):
        # check if the user is blocking for the friend.
        code = random.randint(100000, 999999)
        return UserConfirmationCode.objects.create(code=code, user=self)

    def verify_confirmation_code(self, code):
        # check if the user is blocking for the friend.
        try:
            confirmation = self.confirmation_codes.get(code=code)
            confirmation.set_redeemed()
        except UserConfirmationCode.DoesNotExist:
            raise InvalidConfirmationCodeException

    def send_confirmation_code_email(self, code):
        """ send_welcome_email

        Send a confirmation code email to the user.
        """
        email_template = EmailTemplate.get_confirmation_code_email()
        data = self.generate_confirmation_code_email(email_template, code)

        subject = email_template.subject
        subject = subject.replace('##CONFIRMATION_CODE##', str(code))
        subject = subject.replace('##FIRST_NAME##', self.first_name.title())

        # now store the email
        send_mail(self, subject, data[0], data[1])

    def generate_confirmation_code_email(self, email_template, code):
        '''
        This will generate the welcome email and return the
        rendered value
        '''
        # now let's send something....
        content = email_template.content.replace('##CONFIRMATION_CODE##', str(code))
        soup = BeautifulSoup(content, 'lxml')
        email_txt = soup.get_text()

        html = generate_email(self, 'content/emails/confirmation_code.html',
            {'content': content, 'short_code': email_template.short_code})

        return (html, email_txt)

    # -----------------------------------------------------------------------------
    # start login tracking
    # -----------------------------------------------------------------------------
    def add_login(self, ip_address, country, device):
        """ add_login

        add the user's login. If the user's id is in USER_IGNORE_TRACKING,
        ignore it
        """
        # ignore specific users
        #if str(self.id).replace('-', '') in USER_IGNORE_TRACKING:
        #    return

        UserLogin.objects.create(user=self, ip_address=ip_address, device=device, iso_country=country)
        self.last_login_date = datetime.datetime.now()
        self.save()

    def get_all_logins(self):
        return self.logins.all().order_by('login_date')

    # -----------------------------------------------------------------------------
    # start profile image stuff
    # -----------------------------------------------------------------------------
    def get_profile_image(self):
        ''' return a profile image. make sure they have a user profile object
        first. Later, if no profile image exists, return a default avatar '''

        if hasattr(self, 'userprofileimage'):
            return self.userprofileimage.get_profile_image()

        # No profile image. just return a default
        return static(SystemSetting.get_default_profile_image())

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

    def get_setting(self, setting):

        setting_key = SETTINGS_KEYS[setting]
        item = self.settings.filter(setting=setting_key).first()

        if not item:
            # generate a default
            items_list = SETTINGS_VALUES[setting_key]
            default = None
            for option in items_list:
                default = option.get('default')
                if default:
                    break

            return self.settings.create(
                    setting=SETTINGS_KEYS[settings_key],
                    value=default)

        return item

    def add_email(self, email, is_primary=False):
        if self.emails.filter(email=email).first():
            raise EmailInUseException

        return self.emails.create(email=email, is_primary=is_primary)

    def verify_email(self, id):
        try:
            user_email = self.emails.get(id=id)
            user_email.set_is_verified()
        except UserEmail.DoesNotExist:
            raise InvalidEmailIdException

    def remove_email(self, id):
        try:
            user_email = self.emails.get(id=id)
            if user_email.is_primary:
                # cannot delete the primary email
                raise PrimaryEmailIdException
            user_email.delete()
        except (ValidationError, UserEmail.DoesNotExist):
            raise InvalidEmailIdException

    def get_emails(self):
        return self.emails.all().order_by('-is_primary')

    def set_primary_email(self, id):
        try:
            user_email = self.emails.get(id=id)

            self.email = user_email.email
            self.save()

            user_email.set_is_primary()
        except (ValidationError, UserEmail.DoesNotExist):
            raise InvalidEmailIdException

    # -----------------------------------------------------------------------------
    # Start stuff related to sending emails
    # -----------------------------------------------------------------------------
    def send_welcome_email(self, email_template):
        """ send_welcome_email

        Send a welcome email to the user. Attach a tracker to it to see when
        he has opened it
        """
        data = self.generate_welcome_email(email_template, generate_tracker())

        if EMAIL_BACKEND:
            # now store the email
            send_mail(self, email_template.subject, data[0], data[1])

    def generate_welcome_email(self, email_template, tracker=""):
        '''
        This will generate the welcome email and return the
        rendered value
        '''
        # now let's send something....
        content = email_template.content.replace('##USERNAME##', self.full_name.title())
        soup = BeautifulSoup(content, 'lxml')
        email_txt = soup.get_text()

        html = generate_email(self, 'emails/welcome.html',
            {'content': content, 'short_code': email_template.short_code}, tracker)

        return (html, email_txt)

    # -----------------------------------------------------------------------------
    # Start divesite methods
    # -----------------------------------------------------------------------------
    def add_divesite_recently_viewed(self, divesite):
        '''
        This will generate the welcome email and return the
        rendered value
        '''
        obj, created = self.divesites_recently_viewed.update_or_create(
            divesite=divesite, defaults={},)

        return obj

    def set_divesite_favorite(self, divesite, is_favorite=True):
        '''
        Add a divesite to a user's favorite list
        '''
        if is_favorite:
            obj, _ = self.divesites_favorites.get_or_create(
                divesite=divesite, defaults={})

            return obj
        else:
            self.divesites_favorites.filter(divesite=divesite).delete()


class UserConfirmationCode(UUIDModel):
    user = models.ForeignKey(User, related_name='confirmation_codes', on_delete=models.CASCADE)
    code = models.PositiveIntegerField()
    redeemed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_confirmation_code'

    def set_redeemed(self):
        self.redeemed = True
        self.save()


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    can_add_divesites = models.BooleanField(default=False)
    reputation = models.PositiveSmallIntegerField(default=0)
    is_private = models.BooleanField(default=False)

    secret = models.CharField(max_length=16)

    class Meta:
        db_table = 'account'

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def get_abbreviated_name(self):
        return "%s %s." % (self.first_name, self.last_name[0])

    def __str__(self):
        return self.get_full_name()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])


class UserBuddy(UUIDModel):
    user = models.ForeignKey(User, related_name='buddies', on_delete=models.CASCADE)
    buddy = models.ForeignKey(User, on_delete=models.CASCADE)
    hide = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'user buddies'
        db_table = 'user_buddy'
        unique_together = (('user', 'buddy'), )


class UserBlocked(models.Model):
    user = models.ForeignKey(User, null=True, related_name='blocked', on_delete=models.CASCADE)
    buddy = models.ForeignKey(User, related_name='blocked_friend', on_delete=models.CASCADE)
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'blocked users'
        db_table = 'user_blocked'
        unique_together = (('user', 'buddy'), )


class UserSetting(UUIDModel):
    user = models.ForeignKey(User, null=True, related_name='settings', on_delete=models.CASCADE)
    setting = models.PositiveSmallIntegerField(choices=SETTINGS)
    value = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = 'user settings'
        db_table = 'user_setting'


class UserBuddyRequest(UUIDModel):
    user = models.ForeignKey(User, null=True, related_name='buddy_requests', on_delete=models.CASCADE)
    buddy = models.ForeignKey(User, related_name='buddy_requested', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_buddy_request'
        unique_together = (('user', 'buddy'),)

    def accept_request(self):
        """ accept_request

        accept the buddy request
        """
        self.is_accepted = True
        self.is_active = False
        self.save()


class UserEmail(UUIDModel):
    user = models.ForeignKey(User, related_name='emails', on_delete=models.CASCADE)
    email = models.EmailField(User, unique=True)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'user email addresses'
        db_table = 'user_email'

    def set_is_primary(self):
        self.user.emails.update(is_primary=False)
        self.is_primary = True
        self.save()

    def set_is_verified(self, id):
        user_email = self.emails.get(id=id)
        user_email.is_verified = True
        user_email.save()


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


class UserLogin(UUIDModel):
    """ UserLogin

    Keep a record of the user's login information
    """
    user = models.ForeignKey(User, related_name='logins', on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=512)
    iso_country = models.CharField(max_length=2, default='US')
    login_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_login'
        verbose_name_plural = 'user logins'
        ordering = ['-login_date']

    def __str__(self):
        """ return a string representation of the user login """
        return self.user.get_full_name()


class UserDivesiteFavorite(UUIDModel):
    """ UserFavoriteDivesites

    The user's favorite divesites
    """
    user = models.ForeignKey(User, related_name='divesites_favorites', on_delete=models.CASCADE)
    divesite = models.ForeignKey('divesites.Divesite', on_delete=models.CASCADE)
    notify = models.BooleanField(default=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_divesites_favorites'
        unique_together = (('user', 'divesite'), )


class UserDivesiteRecentlyViewed(UUIDModel):
    """ UserDivesiteRecentlyViewed

    The user's favorite divesites
    """
    user = models.ForeignKey(User, related_name='divesites_recently_viewed', on_delete=models.CASCADE)
    divesite = models.ForeignKey('divesites.Divesite', on_delete=models.CASCADE)
    viewed_date = models.DateTimeField(auto_now=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_divesites_recently_viewed'


class UserRecentActivity(UUIDModel):
    """ UserRecentActivity

    The last thing the user did
    """
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    #divesite = models.ForeignKey('divesites.Divesite', on_delete=models.CASCADE)
    activity_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_recent_activity'
