"""
skm/accounts/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
import pytz
from pprint import pprint
import logging
from geoip import geolite2

from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.signals import user_logged_in

from scuba.accounts.models import User
from scuba.libs.stringutils import StringUtils


@receiver(pre_save, sender=User)
def pre_save_new_user(sender, instance, **kwargs):
    """ pre_save_upgrade_promo

    Some modifications necessary for the campaign once it's uploaded
    """
    logger = logging.getLogger('main')
    key_length = 6

    if not instance.aws_id:
        # generate a short id for this
        instance.aws_id = StringUtils.generate_short_id(User, key_length, 'act', key='aws_id')


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):

    # get the IP address
    ip_address = request.META.get('HTTP_X_REAL_IP')
    tz = None

    if ip_address:
        data = geolite2.lookup(ip_address)
        tz = data.timezone
    else:
        tz = 'America/Los_Angeles'

    timezone.activate(pytz.timezone(tz))
    request.session['timezone'] = tz


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created:
        user_email = instance.add_email(instance.email, True)

        user_email.is_verified = True
        user_email.save()
