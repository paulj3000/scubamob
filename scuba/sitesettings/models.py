import re
from urllib.parse import urljoin
import requests

from django.db import models

from scuba.sitesettings import exceptions
from scuba.libs.models.uuidmodel import UUIDModel
from scuba.sitesettings.exceptions import InvalidConfigurationException
from scuba.sitesettings.settings import (
    SYSTEM_SETTINGS, SYSTEM_APIS, SOCKET_SERVER_SETTINGS,
    LOGBOOK_APIS, SETTINGS_APIS, AWS_APIS, BILLING_APIS, APPS)
from scuba.sitesettings import settings
from scuba.settings import PROFILE_BLANK_URL, BANNER_BLANK_URL


class ApiEndpoint(UUIDModel):
    app = models.CharField(max_length=128, db_index=True, choices=APPS)
    key = models.CharField(max_length=128)
    url = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    class Meta:
        """ define models, fields, etc """
        db_table = 'api_endpoint'
        unique_together = [['app', 'key']]

    @staticmethod
    def get_active_endpoints():
        return ApiEndpoint.objects.filter(is_active=True)


class SystemApi(UUIDModel):
    key = models.CharField(max_length=128, db_index=True, choices=SYSTEM_APIS, unique=True)
    value = models.CharField(max_length=128)
    share_with_chat = models.BooleanField(default=True)

    class Meta:
        """ define models, fields, etc """
        db_table = 'system_api'
        app_label = 'sitesettings'
        ordering = ['key']

    def sync_settings(self):
        if self.share_with_chat:
            chat_server = SystemApi.get_chat_server()
            try:
                data = {
                    'key': self.key,
                    'value': self.value,
                }

                update_url = urljoin(chat_server, 'api/system/setting/update')
                req = requests.post(update_url, json=data)
            except requests.ConnectionError:
                raise exceptions.ChatServerDownException

    @staticmethod
    def get_aws_url_by_key(key, default=None):
        try:
            domain = SystemApi.get_url_by_key('AWS_SERVER')
            endpoint = AWSApi.objects.get(key=key).value
            return urljoin(domain, endpoint)
        except SystemApi.DoesNotExist:
            if default is not None:
                return default

            raise InvalidConfigurationException(f"AWS Api key {key} does not exist")

    @staticmethod
    def get_url_by_key(key, default=None):
        try:
            return SystemApi.objects.get(key=key).value
        except SystemApi.DoesNotExist:
            if default is not None:
                return default

            raise InvalidConfigurationException(f"System Api key {key} does not exist")

    @staticmethod
    def get_billing_authorize_cc_url():
        return SystemApi.get_url_by_key('BILLING_AUTHORIZE_CC')

    @staticmethod
    def get_billing_processors():
        return SystemApi.get_url_by_key('BILLING_PROCESSORS')

    @staticmethod
    def get_aws_cloudfront_url():
        return SystemApi.get_url_by_key('AWS_CLOUDFRONT_URL')

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
    def get_settings_server():
        return SystemApi.get_url_by_key('SETTINGS_SERVER', False)

    @staticmethod
    def get_logbook_server():
        """ get_logbook_server

        Returns:
        string: Returns the base URL for the logbook server
        """
        return SystemApi.get_url_by_key('LOGBOOK_SERVER', False)

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
    def get_default_profile_image():
        return SystemSetting.get_url_by_key('DEFAULT_PROFILE_IMAGE', PROFILE_BLANK_URL)

    @staticmethod
    def get_default_banner_image():
        return SystemSetting.get_url_by_key('DEFAULT_BANNER_IMAGE', BANNER_BLANK_URL)

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


class BaseAPI(UUIDModel):
    def __init__(self, *args, **kwargs):

        if not hasattr(self, 'choices'):
            raise Exception()

        super().__init__(*args, **kwargs)
        self._meta.get_field('key').choices = self.choices

    key = models.CharField(max_length=128, db_index=True, unique=True)
    value = models.CharField(max_length=128)

    def __str__(self):
        """ return a string representation of the page """
        return self.key

    class Meta:
        """ define models, fields, etc """
        abstract = True
        app_label = 'sitesettings'
        ordering = ['key']

    @staticmethod
    def sub_url_userid(url, userid):
        return url.replace(':userid', userid)

    @classmethod
    def get_url(cls, key):
        domain = cls.get_domain()
        obj = cls.objects.get(key=key).value

        return urljoin(domain, obj)

    def get_endpoint(self):
        domain = self.get_domain()
        endpoint = self.value
        url = urljoin(domain, endpoint)
        url = type(self).sub_url_userid(url, 'userid')
        return url

    @classmethod
    def get_domain(cls):
        cls = cls.__name__.upper()
        cls = re.sub('API', '_SERVER', cls)
        return SystemApi.get_url_by_key(cls)


class AlertingApi(BaseAPI):
    choices = settings.ALERTING_APIS

    class Meta:
        db_table = 'alerting_api'


class AWSApi(BaseAPI):
    choices = AWS_APIS

    class Meta:
        db_table = 'aws_api'

    @staticmethod
    def get_s3_upload():
        return SystemApi.get_aws_url_by_key('S3_FILE_UPLOAD')

    @staticmethod
    def get_s3_gen_post_url():
        return SystemApi.get_aws_url_by_key('S3_GEN_POST_URL')

    @staticmethod
    def get_s3_delete():
        return SystemApi.get_aws_url_by_key('S3_FILE_DELETE')


class BillingApi(BaseAPI):
    choices = BILLING_APIS

    class Meta:
        db_table = 'billing_api'


class ChatApi(BaseAPI):
    choices = settings.CHAT_APIS

    class Meta:
        db_table = 'chat_api'

    @classmethod
    def get_all_user_chats(cls, userid):
        url = cls.get_url('GET_ALL_USER_CHATS')

        params = {
            'userId': userid
        }

        try:
            req = requests.get(url, params=params)
            return req.json()
        except (requests.ConnectionError, requests.exceptions.JSONDecodeError):
            raise exceptions.ChatServerDownException

    @classmethod
    def get_all_chat_messages(cls, userid, chatid, limit=100, page=0):
        url = cls.get_url('GET_ALL_CHAT_MESSAGES')

        params = {
            'userId': userid,
            'chatId': chatid,
            'limit': limit,
            'page': page
        }

        try:
            req = requests.get(url, params=params)
            return req.json()
        except (requests.ConnectionError, requests.exceptions.JSONDecodeError):
            raise exceptions.ChatServerDownException

    @classmethod
    def admin_get_all_chats(cls):
        url = cls.get_url('ADMIN_GET_ALL_CHATS')

        try:
            req = requests.get(url)
            return req.json()
        except (requests.ConnectionError, requests.exceptions.JSONDecodeError):
            raise exceptions.ChatServerDownException
from django.core.exceptions import ValidationError


class LogbookApi(BaseAPI):
    choices = settings.LOGBOOK_APIS

    class Meta:
        db_table = 'logbook_api'

    @staticmethod
    def get_all_logbooks(userid):
        domain = SystemApi.get_logbook_server()
        endpoint = LogbookApi.objects.get(key='GET_LOGBOOKS').value

        url = LogbookApi.get_all_logbooks_url(userid)

        try:
            req = requests.get(url)
            return req.json()
        except requests.ConnectionError:
            raise exceptions.LogbookServerDownException

    @staticmethod
    def get_all_logbooks_url(userid):
        domain = SystemApi.get_logbook_server()
        endpoint = LogbookApi.objects.get(key='GET_LOGBOOKS').value

        endpoint = LogbookApi.sub_url_userid(endpoint, userid)
        return urljoin(domain, endpoint)


class SettingsApi(BaseAPI):
    choices = SETTINGS_APIS

    class Meta:
        db_table = 'settings_api'

    @staticmethod
    def get_add_user_setting(userid):
        settings_server = SystemApi.get_settings_server()
        endpoint = SettingsApi.objects.get(key='ADD_USER_SETTING').value

        url = f"{settings_server}{endpoint}"
        return url.replace(':userid', userid)

    @staticmethod
    def get_user_settings_with_options(userid, keys):
        settings_server = SystemApi.get_settings_server()
        endpoint = SettingsApi.objects.get(key='GET_USER_SETTINGS_WITH_OPTIONS').value

        url = f"{settings_server}{endpoint}?setting={(',').join(keys)}"
        return url.replace(':userid', userid)

    @staticmethod
    def get_user_setting_list(userid, keys):
        settings_server = SystemApi.get_settings_server()
        endpoint = SettingsApi.objects.get(key='GET_USER_SETTING_LIST').value

        url = f"{settings_server}{endpoint}?setting={(',').join(keys)}"
        return url.replace(':userid', userid)

    @staticmethod
    def post_user_settings(userid):
        settings_server = SystemApi.get_settings_server()
        endpoint = SettingsApi.objects.get(key='POST_USER_SETTINGS').value

        url = f"{settings_server}{endpoint}"
        return url.replace(':userid', userid)


class APIKey(UUIDModel):
    key = models.CharField(
        db_index=True,
        unique=True,
        max_length=128,
        choices=settings.API_KEYS)
    value = models.CharField(max_length=128)

    class Meta:
        db_table = 'api_key'

    def __str__(self):
        """ return a string representation of the page """
        return self.key

    @staticmethod
    def get_weather_api_key():
        try:
            return APIKey.objects.get(key='WEATHER_API').value
        except APIKey.DoesNotExist:
            raise exceptions.InvalidAPIKeyException

    @staticmethod
    def get_google_maps_key():
        try:
            return APIKey.objects.get(key='GOOGLE_MAPS').value
        except APIKey.DoesNotExist:
            raise exceptions.InvalidAPIKeyException
