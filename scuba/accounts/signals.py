"""
skm/accounts/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
from pathlib import Path

import pytz

from django.conf import settings
from django.db import connection
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_migrate
from django.contrib.auth.signals import user_logged_in

from scuba.accounts.models import User
from scuba.libs.stringutils import StringUtils


@receiver(pre_save, sender=User)
def pre_save_new_user(sender, instance, **kwargs):
    """ pre_save_upgrade_promo

    Some modifications necessary for the campaign once it's uploaded
    """
    key_length = 6

    if not instance.aws_id:
        # generate a short id for this
        instance.aws_id = StringUtils.generate_short_id(User, key_length, 'act', key='aws_id')


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    tz = 'America/Los_Angeles'

    timezone.activate(pytz.timezone(tz))
    request.session['timezone'] = tz
    request.session['zipcode'] = 92107


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created:
        user_email = instance.add_email(instance.email, True)

        user_email.is_verified = True
        user_email.save()


@receiver(post_migrate)
def create_view_profile_view(sender, **kwargs):
    """ create_view_profile_view

    accounts.ViewProfile is `managed = False` -- it maps onto a DB view,
    not a table, so Django's migrate/syncdb never creates it. Run the
    tracked scripts/sql/view_profile.sql here so the view exists after
    any `migrate` (a fresh checkout, entrypoint.sh, or pytest-django's
    test database setup) instead of only on databases someone built by
    hand.

    Guarded on the underlying `user` table actually existing: `accounts`
    has no migrations of its own, so a plain `migrate` (no --run-syncdb)
    never creates it, and CREATE VIEW against a missing table leaves a
    dangling view that SQLite then fails to validate on the next,
    unrelated ALTER TABLE (breaking migrations for every other app).
    Skip quietly rather than risk that -- this just means the view gets
    (re)created the next time migrate runs after the base tables exist.
    """
    if sender.name != 'scuba.accounts':
        return

    if 'user' not in connection.introspection.table_names():
        return

    sql_path = Path(settings.BASE_DIR) / 'scripts' / 'sql' / 'view_profile.sql'
    statements = [s.strip() for s in sql_path.read_text().split(';')]

    with connection.cursor() as cursor:
        for statement in statements:
            if statement:
                cursor.execute(statement)
