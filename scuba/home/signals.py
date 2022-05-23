"""
skm/accounts/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
import logging
from django.dispatch import receiver
from django.db.models.signals import pre_delete

from scuba.home.models import Jumbotron
from scuba.libs.fileutils import FileUtils


@receiver(pre_delete, sender=Jumbotron)
def delete_obj_from_s3(sender, instance, **kwargs):
    """ pre_delete

    Some modifications necessary for the campaign once it's uploaded
    """
    logger = logging.getLogger('main')

    print("FOO")
    print("FOO")
    print("FOO")
    print("FOO")
    print("FOO")
    FileUtils.delete_file_from_s3(instance.filename)
