"""
skm/content/signals.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Add some signal stuff for account creation stuff
"""
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils import timezone

from scuba.content.models import NewsArticle, Article
from scuba.libs.stringutils import StringUtils


@receiver(pre_save, sender=NewsArticle)
def verify_news_article(sender, instance, **kwargs):
    """ verify_news_article

    when saving an article, make sure we have a valid url in the
    title and verify a published date
    """
    instance.url = StringUtils.generate_url_from_string(instance.title)

    # do we need to update the published date
    if not instance.published_date and instance.is_published:
        instance.published_date = timezone.now()


@receiver(pre_save, sender=Article)
def pre_save_new_article(sender, instance, **kwargs):
    """ pre_save_upgrade_promo

    Some modifications necessary for the campaign once it's uploaded
    """
    # logger = logging.getLogger('content')

    if not instance.url:
        url = StringUtils.generate_url_from_string(instance.title) + '-' + \
              StringUtils.generate_time_string()

        # generate a short id for this
        instance.url = url
