import re
from datetime import datetime

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from scuba.aws.models import (
    CodeBuildJob,
    CodeBuildProject,
    CodePipelineState,
    CodePipelineRun,
    InvalidCodeBuildException,
    SNSSubscriptionRequest,
)


class CodeBuildJobSerializer(serializers.ModelSerializer):
    project = serializers.CharField()
    project_arn = serializers.CharField()
    build_status = serializers.CharField()
    build_id = serializers.CharField()
    time = serializers.DateTimeField()

    class Meta:
        """ define models, fields, etc """
        model = CodeBuildJob
        fields = (
            'build_id',
            'build_status',
            'project',
            'project_arn',
            'logs',
            'time',
            'branch',
        )

    @staticmethod
    def validate_build_status(status):
        for _, item in enumerate(CodeBuildJob.BUILD_STATUS_VALUES):
            if item[1] == status:
                return item[0]

        raise InvalidCodeBuildException(f"{status} is invalid")

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        project_name = validated_data['project']
        project, _ = CodeBuildProject.objects.get_or_create(id=validated_data['project_arn'],
                                                            defaults={'project': project_name})

        if validated_data['build_status'] == 0:

            return CodeBuildJob.objects.create(
                id=validated_data['build_id'],
                logs=validated_data['logs'],
                project=project,
                branch=validated_data['branch'],
                start_time=validated_data['time'])

        else:
            if validated_data['build_status'] == 1:
                project.last_successful_build = validated_data['time']
                project.save()

            return CodeBuildJob.objects.filter(id=validated_data['build_id']) \
                               .update(build_status=validated_data['build_status'],
                                       end_time=validated_data['time'])


class CodePipelineStateSerializer(serializers.ModelSerializer):
    execution_id = serializers.UUIDField()
    project_name = serializers.CharField()
    pipeline_arn = serializers.CharField()
    payload = serializers.CharField()
    pipeline_arn = serializers.CharField()
    topic_arn = serializers.CharField()
    notification_rule_arn = serializers.CharField()

    class Meta:
        """ define models, fields, etc """
        model = CodePipelineState
        fields = (
            'notification_rule_arn',
            'execution_id',
            'state',
            'start_time',
            'pipeline_execution_attempt',
            'payload',
            'pipeline_arn',
            'project_name',
            'pipeline_arn',
            'topic_arn',
        )

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        project_name = validated_data['project_name']
        topic_arn = validated_data['topic_arn']
        pipeline, _ = CodePipelineRun \
                      .objects \
                      .get_or_create(id=validated_data['execution_id'],
                                     defaults={'pipeline': project_name,
                                               'run_date': validated_data['start_time'],
                                               'topic_arn': topic_arn})

        state = CodePipelineState \
                .objects \
                .create(
                        pipeline=pipeline,
                        state=validated_data['state'],
                        start_time=validated_data['start_time'],
                        pipeline_execution_attempt=validated_data['pipeline_execution_attempt'],
                        notification_rule_arn=validated_data['notification_rule_arn'],
                        payload=validated_data['payload'],
                )

        return state


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

    @staticmethod
    def validate_signature(data):
        if SNSSubscriptionRequest.objects.filter(signature=data):
            raise serializers.ValidationError(_(f'{data} already exists.'))

        return data

    @staticmethod
    def validate_message_id(data):
        if SNSSubscriptionRequest.objects.filter(message_id=data):
            raise serializers.ValidationError(_(f'{data} already exists.'))

        return data

    @staticmethod
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

        token = re.findall(r"Token=(.*)", validated_data['subscribe_url'])[0]
        validated_data['token'] = token
        return SNSSubscriptionRequest.objects.create(**validated_data)

    def update(self, obj, validated_data):
        raise NotImplementedError
