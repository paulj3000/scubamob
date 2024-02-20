import json

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import rest_framework.status as status
from rest_framework.parsers import JSONParser

from scuba.sitesettings.serializers import SNSSubscriptionRequestSerializer
from scuba.system.serializers import CodebuildJobSerializer
from scuba.libs.rest_framework.parsers import AWSJSONParser


class BuildAPI(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SNSSubscriptionRequestSerializer
    parser_classes = [AWSJSONParser, JSONParser]

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        fh = open("/tmp/build.txt", "a")
        fh.write(json.dumps(request.data) + "\n")
        fh.close()

        if request.data.get('Type') == 'SubscriptionConfirmation':
            serializer = SNSSubscriptionRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        message = json.loads(request.data['Message'])
        detail = message['detail']
        detail['build_status'] = detail['build-status']
        detail['project'] = detail['project-name']
        detail['build_id'] = detail['build-id']
        detail['time'] = message['time']
        detail['branch'] = detail['additional-information']['source-version']

        additional_information = detail['additional-information']
        detail['logs'] = additional_information['logs']['deep-link']

        serializer = CodebuildJobSerializer(data=detail)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
