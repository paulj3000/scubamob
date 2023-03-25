"""
skm/content/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
from datetime import datetime
import logging
import re

from django.dispatch import receiver
from django.db.models.signals import pre_save

from scuba.content.models import NewsArticle


@receiver(pre_save, sender=NewsArticle)
def verify_news_article(sender, instance, **kwargs):
    """ verify_news_article

    when saving an article, make sure we have a valid url in the
    title and verify a published date
    """
    title = re.sub('[^0-9a-zA-Z -]+', '', instance.title)
    instance.url = title.replace(' ', '-').lower()

    # do we need to update the published date
    if not instance.published_date and instance.is_published:
        instance.published_date = datetime.now()
