from datetime import datetime

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from scuba.sitesettings.models import SystemApi, ApiEndpoint, SNSSubscriptionRequest


class SystemApiSerializer(serializers.ModelSerializer):
    class Meta:
        """ define models, fields, etc """
        model = SystemApi
        fields = '__all__'


class SystemEndpointApi(serializers.ModelSerializer):
    class Meta:
        """ define models, fields, etc """
        model = ApiEndpoint
        fields = ('app', 'key', 'url',)


class SNSSubscriptionRequestSerializer(serializers.ModelSerializer):
    MessageId = serializers.CharField(source='message_id')
    TopicArn = serializers.CharField(source='topic_arn')
    SubscribeURL = serializers.CharField(source='subscribe_url')
    Timestamp = serializers.CharField(source='timestamp')
    SignatureVersion = serializers.CharField(source='signature_version')
    Signature = serializers.CharField(source='signature')
    SigningCertURL = serializers.CharField(source='signing_cert_url')

    @staticmethod
    def validate_SigningCertURL(data):
        if SNSSubscriptionRequest.objects.filter(signing_cert_url=data):
            raise serializers.ValidationError(_(f'{data} already exists.'))

        return data

    def validate_signature(data):
        if SNSSubscriptionRequest.objects.filter(signature=data):
            raise serializers.ValidationError(_(f'{data} already exists.'))

        return data

    def validate_message_id(data):
        if SNSSubscriptionRequest.objects.filter(message_id=data):
            raise serializers.ValidationError(_(f'{data} already exists.'))

        return data

    def validate_timestamp(data):
        try:
            return datetime.fromisoformat(data)
        except ValueError:
            raise serializers.ValidationError(_(f'{data} is not a valid timestamp.'))

    class Meta:
        """ define models, fields, etc """
        model = SNSSubscriptionRequest
        fields = ('MessageId',
                  'SigningCertURL',
                  'Signature',
                  'SignatureVersion',
                  'Timestamp',
                  'SubscribeURL',
                  'TopicArn',)

    def create(self, validated_data):
        validated_data['timestamp'] = datetime.strptime(validated_data['timestamp'],
                                                        '%Y-%m-%dT%H:%M:%S.%fZ')

        return SNSSubscriptionRequest.objects.create(**validated_data)

    def update(self, obj, validated_data):
        raise NotImplementedError
