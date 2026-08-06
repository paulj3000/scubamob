from django.db import models
from django.utils import timezone

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.libs.exceptions import InvalidIPAddress


class BlockedCountry(UUIDModel):
    """ Log

    Send an alert to specific users
    """
    name = models.CharField(max_length=64,)
    iso = models.CharField(max_length=12, unique=True)

    class Meta:
        db_table = 'blocked_country'
        verbose_name_plural = 'blocked countries'

    def __str__(self):
        return self.name


class InvalidEmail(UUIDModel):
    ''' what page has the user gone to? '''
    email = models.CharField(max_length=128,)
    ip_address = models.CharField(max_length=128, default='0.0.0.0')
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'invalid_email'

    def __str__(self):
        """ return a string friendly representation of this model """
        return self.email


class BouncedEmail(UUIDModel):
    ''' this user tried signing up w/ a bad email address. Flag it '''
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'bounced_email'

    def __str__(self):
        """ return a string friendly representation of this model """
        return self.user.email


class ImpersonationEvent(UUIDModel):
    ''' audit record of a superuser logging in as another user for support '''

    actor = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='impersonations_started')
    target = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='impersonations_received')
    reason = models.TextField()
    ip_address = models.CharField(max_length=128, default='0.0.0.0')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'impersonation_event'
        ordering = ['-started_at']

    def __str__(self):
        """ return a string friendly representation of this event """
        return f'{self.actor.email} as {self.target.email} ({self.started_at})'

    def mark_ended(self):
        """ close out this event now """
        self.ended_at = timezone.now()
        self.save(update_fields=['ended_at'])


class InvalidSignup(UUIDModel):

    VIEW_SIGNUP = 0
    VIEW_LOGIN = 1
    VIEW_CONTACT_US = 2

    VIEW_CHOICES = (
        (VIEW_SIGNUP, 'Signup'),
        (VIEW_LOGIN, 'Login'),
        (VIEW_CONTACT_US, 'Contact Us'),
    )

    email = models.CharField(max_length=128,)
    ip_address = models.CharField(max_length=128, default='0.0.0.0')
    view = models.PositiveSmallIntegerField(choices=VIEW_CHOICES)
    blocked_country = models.ForeignKey('security.BlockedCountry', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ define database tables, etc """
        db_table = 'invalid_signup'
        verbose_name_plural = 'invalid signups'
        ordering = ['-created_date']
