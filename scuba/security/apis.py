import logging

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import rest_framework.status as status

from scuba.libs.aws.sns import SNSVerificationError, verify_signature
from scuba.sitesettings.serializers import SNSSubscriptionRequestSerializer

logger = logging.getLogger(__name__)


class BouncedEmailsAPI(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SNSSubscriptionRequestSerializer

    def post(self, request):
        """ post

        Handle an inbound SES-bounce SNS notification. Only messages
        carrying a valid AWS SNS signature are processed.
        """
        try:
            verify_signature(request.data)
        except SNSVerificationError as exc:
            logger.warning('Rejected unverified bounced-email SNS message: %s', exc)
            return Response(status=status.HTTP_403_FORBIDDEN)

        if request.data.get('Type') == 'SubscriptionConfirmation':
            serializer = SNSSubscriptionRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        logger.info('Verified bounced-email SNS notification: %s', request.data)

        return Response(status=200)
