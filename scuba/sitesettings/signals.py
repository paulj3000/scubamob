"""
skm/accounts/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
import requests
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save

from scuba.libs.exceptions import ChatServerDownException
from scuba.sitesettings.models import SystemApi, SystemSetting


@receiver(post_save, sender=SystemApi)
def validate_is_active(sender, instance, **kwargs):
    """ post_save

    Some modifications necessary for the campaign once it's uploaded
    """
    logger = logging.getLogger('main')

    chat_server = SystemApi.get_chat_server()

    # force the chat server to update
    if SystemSetting.get_chat_server_active():
        try:
            instance.sync_settings()
        except ChatServerDownException:
            print("cannot update settings")
