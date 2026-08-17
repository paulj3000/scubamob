import datetime
import random

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags
from django.db.models import Q
from django.templatetags.static import static
from django.core.exceptions import ValidationError

from rest_framework.authtoken.models import Token

from scuba.accounts.settings import SETTINGS_KEYS, SETTINGS_VALUES
from scuba.libs.models.uuidmodel import UUIDModel
from scuba.accounts.exceptions import (
    InvalidEmailIdException, InvalidUserIdException,
    PrimaryEmailIdException, EmailInUseException, InvalidConfirmationCodeException)
from scuba.accounts.settings import SETTINGS
from scuba.divesites.models import Divesite
from scuba.settings import (
    AWS_CLOUDFRONT, EMAIL_BACKEND, PROFILE_BLANK_URL, SITE_TITLE,
    MAGIC_LINK_TOKEN_TTL_MINUTES)

from scuba.libs.mail import generate_email, send_mail


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        if not extra_fields.get('username'):
            raise ValueError('The given username must be set')

        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(email=email, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # return the new user
        return user

    def create_superuser(self, email, password, **extra_fields):
        ''' override the create superuser function '''
        user = self.create_user(email, password=password, **extra_fields)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, UUIDModel):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    username = models.CharField(max_length=40, unique=True, db_index=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    aws_id = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(default='1970-04-01')
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
    REQUIRED_FIELDS = ['username']

    @property
    def profile_image(self):
        return self.get_profile_image()

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_premier(self):
        return hasattr(self, 'userispremier')

    def get_full_name(self):
        """ get_full_name

        get the user's full name
        """
        return f"{self.first_name.strip()} {self.last_name.strip()}"

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
    # start Buddy stuff
    # -----------------------------------------------------------------------------
    def get_active_buddy_requests(self):
        ''' get_active_buddy_requests

        Return the pending buddy requests sent to this user.
        '''
        return self.buddy_requested.filter(is_active=True).order_by('user__first_name')

    def get_buddy(self, buddy):
        return UserBuddy.objects.filter(
            Q(buddy=buddy) | Q(user=buddy)).first()

    def get_my_buddy(self, buddy_id):
        return self.buddies.filter(buddy__id=buddy_id)

    def get_buddies_count(self):
        # get all of the current buddies
        return self.buddies.all().count()

    def get_all_buddies(self):
        # return all of the buddies that is not us!
        return self.buddies.all()

    def get_all_buddies_recent_activity(self):
        # return all of the buddies that is not us!
        return self.buddies.all().order_by('-user__activities__activity_date')

    def get_buddies_feed(self, limit=10):
        """ get_buddies_feed

        return the most recent non-private feed activity (reviews,
        checkins) posted by any of this user's buddies
        """
        buddy_ids = self.buddies.values_list('buddy_id', flat=True)
        return UserFeed.objects.filter(
            user_id__in=buddy_ids, is_private=False
        ).select_related('user').order_by('-created')[:limit]

    def add_buddy(self, buddy):
        """ add_buddy

        add a buddy for the user
        """
        retval = self.buddies.create(buddy=buddy)
        buddy.buddies.create(buddy=self)
        return retval

    def remove_buddy(self, buddy):
        """ remove_buddy

        add the buddy for the user for the user
        """
        self.buddies.filter(buddy=buddy).delete()
        buddy.buddies.filter(buddy=self).delete()

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

            data = self.buddy_requested.filter(
                buddy=self, is_active=True, is_deleted=False).first()
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
        # remove the buddy if he's already a buddy
        self.remove_buddy(buddy)

        # remove all buddy requests
        UserBuddyRequest.objects.filter(
            Q(user=buddy, buddy=self) | Q(user=self, buddy=buddy)).delete()

        # get all of the current buddies
        blocked, _ = UserBlocked.objects.get_or_create(
            user=self, buddy=buddy, blocked_by=self)

        return blocked

    def follow_buddy(self, buddy, follow):
        # set the user buddy flag to follow
        self.buddies.filter(buddy=buddy).follow(follow)

    def get_blocked_buddies(self):
        # get all of the current buddies
        return self.blocked_user.order_by('friend__first_name')

    def is_blocked(self, buddy):
        # check if the user is blocking for the friend.
        return UserBlocked.objects.filter(
            Q(user=buddy, buddy=self) | Q(user=self, buddy=buddy)).count()

    # -----------------------------------------------------------------------------
    # start confirmation code stuff
    # -----------------------------------------------------------------------------
    def generate_confirmation_code(self):
        # check if the user is blocking for the friend.
        code = random.randint(100000, 999999)
        return UserConfirmationCode.objects.create(code=code, user=self)

    def confirm_user(self):
        """ confirm_user

        confirm the user
        """
        self.confirmed = True
        self.save()

    def verify_confirmation_code(self, code):
        # check if the user is blocking for the friend.
        try:
            confirmation = self.confirmation_codes.get(code=code)
            confirmation.set_redeemed()
        except UserConfirmationCode.DoesNotExist:
            raise InvalidConfirmationCodeException

    def send_confirmation_code_email(self, code):
        """ send_confirmation_code_email

        Send a confirmation code email to the user.
        """
        html, text = self.generate_confirmation_code_email(code)
        subject = f"Your {SITE_TITLE} confirmation code is {code}"

        # now store the email
        send_mail(self, subject, html, text)

    def generate_confirmation_code_email(self, code):
        '''
        This will generate the confirmation code email and return the
        rendered value
        '''
        content = f"Your confirmation code is <strong>{code}</strong>."

        html = generate_email(
            self, 'content/emails/confirmation_code.html',
            {'content': content, 'short_code': f'Your {SITE_TITLE} confirmation code'})

        return (html, strip_tags(content))

    # -----------------------------------------------------------------------------
    # start feed stuff
    # -----------------------------------------------------------------------------
    def get_feed(self):
        '''
        return all of the user's activity, (as a feed)
        '''
        return self.feed.all()

    def add_review_to_feed(self, id):
        return self.add_to_feed(id, 0)

    def get_feed_review(self, id):
        return self.get_from_feed(id, 0)

    def add_checkin_to_feed(self, id):
        return self.add_to_feed(id, 1)

    def get_feed_checkin(self, id):
        return self.get_from_feed(id, 1)

    def add_to_feed(self, id, instance_type):
        '''
        return all of the user's activity, (as a feed)
        '''
        return self.feed.create(instance_id=id, instance_type=instance_type)

    def get_from_feed(self, id, instance_type):
        '''
        return all of the user's activity, (as a feed)
        '''
        return self.feed.filter(instance_id=id, instance_type=instance_type).first()

    # -----------------------------------------------------------------------------
    # start location tracking
    # -----------------------------------------------------------------------------
    def get_active_location(self):
        """ get_default_location

        What is the default location
        ignore it
        """
        return self.locations.filter(is_active=True).first()

    # -----------------------------------------------------------------------------
    # start login tracking
    # -----------------------------------------------------------------------------
    def add_login(self, ip_address, country, device):
        """ add_login

        add the user's login. If the user's id is in USER_IGNORE_TRACKING,
        ignore it
        """
        # ignore specific users
        # if str(self.id).replace('-', '') in USER_IGNORE_TRACKING:
        #    return

        UserLogin.objects.create(
            user=self, ip_address=ip_address, device=device, iso_country=country)
        self.last_login_date = datetime.datetime.now()
        self.save()

    def get_all_logins(self):
        return self.logins.all().order_by('login_date')

    def set_is_premier(self, is_premier):
        if is_premier:
            if not hasattr(self, 'userispremier'):
                UserIsPremier.objects.create(user=self)
        else:
            UserIsPremier.objects.filter(user=self).delete()

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

            return self.settings.create(setting=setting_key, value=default)

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
    def send_welcome_email(self):
        """ send_welcome_email

        Send a welcome email to the user.
        """
        html, text = self.generate_welcome_email()

        if EMAIL_BACKEND:
            # now store the email
            send_mail(self, f"Welcome to {SITE_TITLE}!", html, text)

    def generate_welcome_email(self):
        '''
        This will generate the welcome email and return the
        rendered value
        '''
        content = f"Welcome to {SITE_TITLE}, {self.get_full_name().title()}!"

        html = generate_email(
            self,
            'content/emails/welcome.html',
            {'content': content, 'short_code': f'Welcome to {SITE_TITLE}'})

        return (html, strip_tags(content))

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

    def get_divesite_favorites(self):
        '''
        Get favorite divesites
        '''
        retval = []

        for item in Divesite.objects.filter(
                is_active=True, followers__user=self):
            retval.append(item.pk_as_str)

        # return the divesites
        return retval

    # -----------------------------------------------------------------------------
    # start photos and albums stuff
    # -----------------------------------------------------------------------------
    def get_photos(self):
        ''' return a profile image. make sure they have a user profile object
        first. Later, if no profile image exists, return a default avatar '''

        return self.media.all()

    # -----------------------------------------------------------------------------
    # start following stuff
    def set_follow_user(self, user, is_following):
        ''' return a profile image. make sure they have a user profile object
        first. Later, if no profile image exists, return a default avatar '''
        obj, _ = UserFollower.objects.update_or_create(user=self,
                                                       follower=user,
                                                       defaults={'is_following': is_following})

        # return the object
        return obj

    def create_collection(self, name, is_public):
        ''' return a profile image. make sure they have a user profile object
        first. Later, if no profile image exists, return a default avatar '''
        return self.collections.create(name=name, is_public=is_public)

    def get_collections(self):
        ''' return all of the collections for this user. order them by name '''
        return self.collections.all().order_by('name')

    def add_signup_country(self, iso_country):
        UserSignupCountry.objects.create(user=self, iso_country=iso_country)


class UserFeed(UUIDModel):
    FEED_VALUES = {
        (0, 'Review'),
        (1, 'Checkin'),
    }

    user = models.ForeignKey(User, related_name='feed', on_delete=models.CASCADE)
    instance_type = models.PositiveSmallIntegerField(choices=FEED_VALUES)
    instance_id = models.UUIDField()
    is_private = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_feed'
        unique_together = (('instance_id', 'instance_type', 'user'), )


class FlagOption(UUIDModel):
    FLAG_TYPES = {
        (0, 'Review'),
        (1, 'Checkin'),
    }

    flag = models.CharField(max_length=128)
    instance_type = models.PositiveSmallIntegerField(choices=FLAG_TYPES)

    class Meta:
        db_table = 'flag_option'


class UserFeedFlagged(UUIDModel):
    user = models.ForeignKey(User, related_name='flags', on_delete=models.CASCADE)
    user_feed = models.ForeignKey(UserFeed, related_name='flags', on_delete=models.CASCADE)
    flag = models.ForeignKey(FlagOption, on_delete=models.CASCADE)
    reason = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'user feed flagged'
        db_table = 'user_feed_flagged'
        unique_together = (('user_feed', 'user'), )


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


class MagicLinkToken(UUIDModel):
    """ MagicLinkToken

    A one-time, expiring token used to sign a user in without a password
    ("magic link" / passwordless login). Only the salted hash of the raw
    token is ever persisted.
    """
    user = models.ForeignKey(User, related_name='magic_link_tokens', on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, db_index=True)
    redeemed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_magic_link_token'

    def set_redeemed(self):
        self.redeemed = True
        self.save()

    def is_expired(self):
        return timezone.now() > self.created + datetime.timedelta(minutes=MAGIC_LINK_TOKEN_TTL_MINUTES)


class UserFollower(UUIDModel):
    """ UserFollower

    Who is following who
    """
    user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    is_following = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'user followers'
        db_table = 'user_follower'
        unique_together = (('user', 'follower'), )


class UserBuddy(UUIDModel):
    user = models.ForeignKey(User, related_name='buddies', on_delete=models.CASCADE)
    buddy = models.ForeignKey(User, on_delete=models.CASCADE)

    # kind of like a "don't see my stories" thing
    hide = models.BooleanField(default=False)

    # is following: This is different from the UserFollower flag. This
    # version of "is_following" means they're still buddies, but the buddy is muted
    is_following = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'user buddies'
        db_table = 'user_buddy'
        unique_together = (('user', 'buddy'), )

    def set_follow(self, follow):
        self.is_following = follow
        self.save()


class UserBuddyRemove(UUIDModel):
    user = models.ForeignKey(User, related_name='removed', on_delete=models.CASCADE)
    buddy = models.ForeignKey(User, on_delete=models.CASCADE)
    removed_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'user buddies removed'
        db_table = 'user_buddy_removed'


class UserBlocked(models.Model):
    user = models.ForeignKey(User, null=True, related_name='blocked', on_delete=models.CASCADE)
    buddy = models.ForeignKey(User, related_name='blocked_buddy', on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, related_name='buddy_requests', on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, related_name='locations', on_delete=models.CASCADE)
    postal_code = models.CharField(max_length=16)
    city = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_location'


class UserIsPremier(UUIDModel):
    """ UserLocation

    Keep a representation of the user's profile image
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_is_premier'


class UserSignupCountry(UUIDModel):
    """ UserSignUpCountry
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    iso_country = models.CharField(max_length=5)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_signup_country'
        verbose_name_plural = 'user signup country'


class UserHidden(UUIDModel):
    """ UserHidden

    Is the user hidden?
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_hidden'


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
        return self.image.replace('profiles/', '')

    def get_profile_image(self):
        """ get_profile_image

        sanitize the profile image. This will return the full url path
        of the profile image, sans the 'profiles/' prefix
        """
        return f"{AWS_CLOUDFRONT}{self.image_cleaned}"


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
    user = models.ForeignKey(
        User, related_name='divesites_recently_viewed', on_delete=models.CASCADE)
    divesite = models.ForeignKey('divesites.Divesite', on_delete=models.CASCADE)
    viewed_date = models.DateTimeField(auto_now=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_divesites_recently_viewed'


class UserCollection(UUIDModel):
    """ UserDivesiteCollection

    The user's favorite divesites
    """
    user = models.ForeignKey(User, related_name='collections', on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    is_public = models.BooleanField(default=False)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_collection'

    def add_to_collection(self, instance_type, instance_id):
        return self.items.create(instance_type=instance_type, instance_id=instance_id)


class UserCollectionItem(UUIDModel):
    COLLECTION_VALUES = {
        (0, 'Divesite'),
        (1, 'Dive Shop'),
    }

    collection = models.ForeignKey(UserCollection, related_name='items', on_delete=models.CASCADE)
    instance_type = models.PositiveSmallIntegerField(choices=COLLECTION_VALUES)
    instance_id = models.UUIDField()

    class Meta:
        """ define database tables, etc """
        db_table = 'user_collection_item'
        unique_together = (('instance_id', 'instance_type', 'collection'), )


class UserRecentActivity(UUIDModel):
    """ UserRecentActivity

    The last thing the user did
    """
    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    # divesite = models.ForeignKey('divesites.Divesite', on_delete=models.CASCADE)
    activity_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'user_recent_activity'


class ViewProfile(UUIDModel):
    """ ViewProfile

    The profile of the user
    """
    username = models.CharField(max_length=40, unique=True, db_index=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    location = models.CharField(max_length=512)
    profile_image = models.CharField(max_length=128)
    followers_count = models.PositiveSmallIntegerField(default=0)
    buddy_count = models.PositiveSmallIntegerField(default=0)
    reviews_count = models.PositiveSmallIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        """ define database tables, etc """
        db_table = 'view_profile'
        managed = False

    def get_full_name(self):
        """ get_full_name

        get the user's full name
        """
        return f"{self.first_name.strip()} {self.last_name.strip()}"

    def get_is_following(self, user):
        """ get_full_name

        get the user's full name
        """
        return True if UserFollower.objects.filter(id=self.id, user=user).count() else False

    def get_profile_image(self):
        ''' return a profile image. make sure they have a user profile object
        first. Later, if no profile image exists, return a default avatar '''

        if self.profile_image:
            return f"{AWS_CLOUDFRONT}{self.profile_image.replace('profiles/', '')}"

        return static(PROFILE_BLANK_URL)

    @property
    def is_hidden(self):
        ''' return a profile image. make sure they have a user profile object
        first. Later, if no profile image exists, return a default avatar '''

        return True if UserHidden.objects.filter(id=self.id).count() else False
