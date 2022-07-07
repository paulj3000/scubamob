"""
skm/accounts/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
import logging
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete

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
