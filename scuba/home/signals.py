"""
skm/accounts/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save

from scuba.home.models import Jumbotron
from scuba.libs.fileutils import FileUtils


@receiver(pre_delete, sender=Jumbotron)
def delete_obj_from_s3(sender, instance, **kwargs):
    """ pre_delete

    Some modifications necessary for the campaign once it's uploaded
    """
    FileUtils.delete_file_from_s3(instance.filename)


@receiver(pre_save, sender=Jumbotron)
def validate_is_active(sender, instance, **kwargs):
    """ post_save

    Some modifications necessary for the campaign once it's uploaded
    """
    # verify there is an active jumbotron. If there is not, set this one
    # to active
    if not Jumbotron.objects.filter(is_active=True).count():
        instance.is_active = True
