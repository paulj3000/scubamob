"""
skm/legal/models.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

The models for the legal pages stuff
"""
from django.db import models
from django.db.models import Max

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.libs.models.awsmodel import AWSModel
from scuba.settings import AWS_CLOUDFRONT
from scuba.content.exceptions import InvalidConfigrationException


class Page(UUIDModel):
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=32)
    content = models.TextField()

    class Meta:
        """ define models, fields, etc """
        db_table = 'page'

    def __str__(self):
        """ return a string representation of the page """
        return self.name


class EmailTemplate(UUIDModel):
    """
    EmailTemplate

    Allow dickhead to define the welcome emails
    """
    EMAIL_WELCOME_FREE = 0
    EMAIL_WELCOME_PREMIUM = 1
    EMAIL_TEMPLATES = (
        (EMAIL_WELCOME_FREE, 'Welcome Free Account'),
        (EMAIL_WELCOME_PREMIUM, 'Welcome Premium Account'),
    )

    template_type = models.PositiveSmallIntegerField(choices=EMAIL_TEMPLATES, unique=True)
    subject = models.CharField(max_length=128)
    short_code = models.CharField(max_length=128)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        """ define models, fields, etc """
        db_table = 'email_template'

    def __str__(self):
        """ return a string representation of the page """
        return self.get_template_type_display()

    @classmethod
    def get_welcome_email(cls):
        email = cls.objects.filter(template_type=cls.EMAIL_WELCOME_FREE).first()

        # do we have a valid email
        if email:
            return email

        # we don't have a valid configuration. Throw an exception
        raise InvalidConfigrationException("Missing free email template")


class Image(AWSModel):
    """ Image

    This is for all images updated to the website for content purposes
    """
    title = models.CharField(max_length=64)
    class Meta:
        """ define models, fields, etc """
        verbose_name_plural = 'images'
        db_table = 'image'

    @property
    def url(self):
        filename = self.filename.replace('uploaded_images/', '')
        return f"{AWS_CLOUDFRONT}{filename}"


class FAQSection(models.Model):
    title = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField()

    class Meta:
        """ define models, fields, etc """
        db_table = 'faq_section'

    def __str__(self):
        """ return a string representation of faq section """
        return self.title

    def get_entries(self):
        return self.faq_entries.all().order_by('position')

    def save(self, *args, **kwargs):
        if not self.position:
            tst = FAQEntry.objects.filter(faq_section=self).aggregate(Max('position'))
            pos = tst.get('position__max') or -1
            self.position = pos

        super().save(*args, **kwargs)


class FAQEntry(models.Model):
    faq_section = models.ForeignKey(FAQSection,
                                    related_name='faq_entries',
                                    on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    position = models.PositiveSmallIntegerField()

    entry_pos = 0

    def set_entry_pos(self, pos):
        self.entry_pos = pos

    class Meta:
        """ define models, fields, etc """
        verbose_name_plural = 'faq entries'
        db_table = 'faq_entry'

    def __str__(self):
        """ return a string representation of faq entry """
        return self.title

    def save(self, *args, **kwargs):

        if not self.position:
            pos = FAQEntry.objects.filter(faq_section=self.faq_section).aggregate(Max('position'))


class NewsArticle(UUIDModel):
    title = models.CharField(max_length=128, unique=True)
    url = models.CharField(max_length=32, editable=False, db_index=True)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, editable=False)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(editable=False, null=True)
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        """ define models, fields, etc """
        db_table = 'news_article'

    def __str__(self):
        """ return a string representation of the page """
        return self.title

    @classmethod
    def get_published_articles(cls, page=0, limit=10):
        """ get_published_articles

        get all of the published articles
        """
        return cls.objects.filter(is_published=True).order_by('-last_modified')
