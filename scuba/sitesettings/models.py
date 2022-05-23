from urllib.parse import urljoin

from django.db import models
from django.db.models import Q

from scuba.libs.models.uuidmodel import UUIDModel
from scuba.sitesettings.exceptions import InvalidConfigurationException
from scuba.sitesettings.settings import SITE_SETTINGS, ALERTING_API_SETTINGS


class SystemApi(UUIDModel):
    key = models.CharField(max_length=128, db_index=True, choices=SITE_SETTINGS)
    url = models.CharField(max_length=128)

    class Meta:
        """ define models, fields, etc """
        db_table = 'system_api'
        app_label = 'sitesettings'
        ordering = ['key',]

    @staticmethod
    def get_url_by_key(key):
        try:
            return SystemApi.objects.get(key=key).url
        except SystemApi.DoesNotExist:
            raise InvalidConfigurationException(f"System Api key {key} does not exist")

    def get_s3_upload():
        return SystemApi.get_url_by_key('AWS_S3_UPLOAD')

    def get_s3_delete():
        return SystemApi.get_url_by_key('AWS_S3_DELETE')

    @staticmethod
    def get_billing_authorize_cc_url():
        return SystemApi.get_url_by_key('BILLING_AUTHORIZE_CC')

    @staticmethod
    def get_billing_processors():
        return SystemApi.get_url_by_key('BILLING_PROCESSORS')

    @staticmethod
    def get_default_layout():
        return SystemApi.get_url_by_key('LAYOUT_DEFAULT_LAYOUT')

    @staticmethod
    def get_page_default():
        return SystemApi.get_url_by_key('LAYOUT_PAGE_DEFAULT')

    # -----------------------------------------------------------------------------
    # start Alerting APIs
    # -----------------------------------------------------------------------------
    @staticmethod
    def get_alerting_url():
        return SystemApi.get_url_by_key('ALERTING_URL')

    @staticmethod
    def get_alert_notify_staff():
        endpoint = SystemApi.get_url_by_key('ALERTING_NOTIFY_STAFF')
        domain = SystemApi.get_url_by_key('ALERTING_URL')

        return urljoin(domain, endpoint)


    # -----------------------------------------------------------------------------
    # start API group stuff
    # -----------------------------------------------------------------------------
    @staticmethod
    def get_alerting_apis():
        return SystemApi.objects.filter(key__in=ALERTING_API_SETTINGS)

    def __str__(self):
        """ return a string representation of the page """
        return self.key


class SystemQueue(UUIDModel):
    key = models.CharField(max_length=128, db_index=True)
    queue = models.CharField(max_length=128)

    class Meta:
        """ define models, fields, etc """
        db_table = 'system_queue'
        app_label = 'sitesettings'

    @staticmethod
    def get_billing_authorize_cc_url():
        return SystemApi.get_url_by_key('QUEUE_MARKETPLACE')
