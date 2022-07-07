from datetime import datetime, timedelta
import random
import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from scuba.sitesettings.models import SystemApi


class SystemApiSerializer(serializers.ModelSerializer):
    class Meta:
        """ define models, fields, etc """
        model = SystemApi
        fields = '__all__'

