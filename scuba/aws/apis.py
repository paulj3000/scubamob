import json
import logging

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import rest_framework.status as status
from rest_framework.parsers import JSONParser

from scuba.sitesettings.serializers import SNSSubscriptionRequestSerializer
from scuba.aws.serializers import (
    CodePipelineStateSerializer,
    CodeBuildJobSerializer,
)

from scuba.libs.aws.sns import SNSVerificationError, verify_signature
from scuba.libs.rest_framework.parsers import AWSJSONParser

logger = logging.getLogger(__name__)


class CodeBuildAPI(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SNSSubscriptionRequestSerializer
    parser_classes = [AWSJSONParser, JSONParser]

    def post(self, request):
        """ post

        Handle an inbound AWS CodeBuild SNS notification. Only messages
        carrying a valid AWS SNS signature are processed.
        """
        try:
            verify_signature(request.data)
        except SNSVerificationError as exc:
            logger.warning('Rejected unverified CodeBuild SNS message: %s', exc)
            return Response(status=status.HTTP_403_FORBIDDEN)

        logger.debug('Verified CodeBuild SNS message: %s', request.data)

        if request.data.get('Type') == 'SubscriptionConfirmation':
            serializer = SNSSubscriptionRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        try:
            message = json.loads(request.data['Message'])
            detail = message['detail']
            detail['build_status'] = detail['build-status']
            detail['project'] = detail['project-name']
            detail['project_arn'] = detail['build-id'].split('/')[0]
            detail['build_id'] = detail['build-id']
            detail['time'] = message['time']
            detail['branch'] = detail['additional-information']['source-version']

            additional_information = detail['additional-information']
            detail['logs'] = additional_information['logs']['deep-link']

            serializer = CodeBuildJobSerializer(data=detail)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CodePipelineAPI(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SNSSubscriptionRequestSerializer
    parser_classes = [AWSJSONParser, JSONParser]

    def post(self, request):
        """ post

        Handle an inbound AWS CodePipeline SNS notification. Only messages
        carrying a valid AWS SNS signature are processed.
        """
        try:
            verify_signature(request.data)
        except SNSVerificationError as exc:
            logger.warning('Rejected unverified CodePipeline SNS message: %s', exc)
            return Response(status=status.HTTP_403_FORBIDDEN)

        logger.debug('Verified CodePipeline SNS message: %s', request.data)

        if request.data.get('Type') == 'SubscriptionConfirmation':
            serializer = SNSSubscriptionRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        try:
            message = json.loads(request.data['Message'])
            detail = message['detail']
            detail['pipeline_execution_attempt'] = detail['pipeline-execution-attempt']
            detail['project_name'] = detail['pipeline']
            detail['start_time'] = detail['start-time']
            detail['execution_id'] = detail['execution-id']
            detail['notification_rule_arn'] = message.get('notificationRuleArn')
            detail['topic_arn'] = request.data['TopicArn']
            detail['payload'] = json.dumps(request.data)

            for arn in message.get('resources'):
                detail['pipeline_arn'] = arn
                serializer = CodePipelineStateSerializer(data=detail)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
