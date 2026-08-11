from rest_framework import serializers

from scuba.sitesettings.models import SystemApi, Endpoint


class SystemApiSerializer(serializers.ModelSerializer):
    class Meta:
        """ define models, fields, etc """
        model = SystemApi
        fields = '__all__'


class SystemEndpointApi(serializers.ModelSerializer):
    class Meta:
        """ define models, fields, etc """
        model = Endpoint
        fields = ('key', 'url',)
