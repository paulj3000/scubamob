from urllib.parse import urljoin
import requests

from django.db import models

from scuba.libs.exceptions import ChatServerDownException
from scuba.libs.models.uuidmodel import UUIDModel
from scuba.sitesettings.exceptions import InvalidConfigurationException
from scuba.sitesettings.settings import SYSTEM_SETTINGS, SYSTEM_APIS, SOCKET_SERVER_SETTINGS, DIVELOG_APIS


class SystemApi(UUIDModel):
    key = models.CharField(max_length=128, db_index=True, choices=SYSTEM_APIS, unique=True)
    value = models.CharField(max_length=128)
    share_with_chat = models.BooleanField(default=True)

    class Meta:
        """ define models, fields, etc """
        db_table = 'system_api'
        app_label = 'sitesettings'
        ordering = ['key',]

    def sync_settings(self):
        if self.share_with_chat:
            chat_server = SystemApi.get_chat_server()
            try:
                data = {
                    'key': self.key,
                    'value': self.value,
                }

                update_url = f"{chat_server}api/system/setting/update"
                req = requests.post(update_url, json=data)
            except requests.ConnectionError:
                raise ChatServerDownException

    @staticmethod
    def get_url_by_key(key, default=None):
        try:
            return SystemApi.objects.get(key=key).value
        except SystemApi.DoesNotExist:
            if default is not None:
                return default

            raise InvalidConfigurationException(f"System Api key {key} does not exist")

    def get_aws_cloudfront_url():
        return SystemApi.get_url_by_key('AWS_CLOUDFRONT_URL')

    def get_aws_s3_bucket():
        return SystemApi.get_url_by_key('AWS_S3_BUCKET')

    def get_s3_upload():
        return SystemApi.get_url_by_key('AWS_S3_FILE_UPLOAD')

    def get_s3_gen_post_url():
        return SystemApi.get_url_by_key('AWS_S3_GEN_POST_URL')

    def get_s3_delete():
        return SystemApi.get_url_by_key('AWS_S3_FILE_DELETE')

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

    def get_alerting_alerts():
        endpoint = SystemApi.get_url_by_key('ALERTING_ALERTS')
        return SystemApi.get_alerting_endpoint(endpoint)

    def get_alerting_buddy_request():
        endpoint = SystemApi.get_url_by_key('ALERTING_BUDDY_REQUEST')
        return SystemApi.get_alerting_endpoint(endpoint)

    @staticmethod
    def get_chat_server():
        return SystemApi.get_url_by_key('CHAT_SERVER', False)

    @staticmethod
    def get_divelog_server():
        return SystemApi.get_url_by_key('DIVELOG_SERVER', False)

    @staticmethod
    def get_alerting_endpoint(endpoint):
        domain = SystemApi.get_url_by_key('ALERTING_SERVER')
        return urljoin(domain, endpoint)

    @staticmethod
    def get_alert_notify_staff():
        endpoint = SystemApi.get_url_by_key('ALERTING_NOTIFY_STAFF')
        domain = SystemApi.get_url_by_key('ALERTING_URL')

        return urljoin(domain, endpoint)

    # -----------------------------------------------------------------------------
    # start API group stuff
    # -----------------------------------------------------------------------------
    @staticmethod
    def get_socket_server_settings():
        return SystemApi.objects.filter(key__in=SOCKET_SERVER_SETTINGS)

    def __str__(self):
        """ return a string representation of the page """
        return self.key


class SystemSetting(UUIDModel):
    key = models.CharField(max_length=128, db_index=True, choices=SYSTEM_SETTINGS, unique=True)
    value = models.CharField(max_length=128)

    class Meta:
        """ define models, fields, etc """
        db_table = 'system_setting'

    @staticmethod
    def get_chat_server_active():
        return SystemSetting.get_url_by_key('CHAT_SERVER_ACTIVE', False)

    @staticmethod
    def get_url_by_key(key, default=None):
        try:
            return SystemSetting.objects.get(key=key).value
        except SystemSetting.DoesNotExist:
            if default is not None:
                return default

            raise InvalidConfigurationException(f"System setting key {key} does not exist")

    def __str__(self):
        """ return a string representation of the page """
        return self.key


class DiveLogApi(UUIDModel):
    key = models.CharField(max_length=128, db_index=True, choices=DIVELOG_APIS, unique=True)
    value = models.CharField(max_length=128)

    def __str__(self):
        """ return a string representation of the page """
        return self.key

    class Meta:
        """ define models, fields, etc """
        db_table = 'divelog_api'
        app_label = 'sitesettings'
        ordering = ['key',]

    @staticmethod
    def get_divelog_url():
        divelog_server = SystemApi.get_divelog_server()
        url = SystemApi.objects.get(key='GET_DIVELOGS').value
        return f"{divelog_server}/{url}"
