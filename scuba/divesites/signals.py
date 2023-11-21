"""
skm/divesites/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from scuba.divesites.models import DivesiteCheckin


@receiver(pre_delete, sender=DivesiteCheckin)
def pre_delete_checkin(sender, instance, **kwargs):
    """ pre_save_upgrade_promo

    Some modifications necessary for the campaign once it's uploaded
    """
    instance.user.feed.filter(instance_id=instance.id).delete()
