import json

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import rest_framework.status as status

from scuba.sitesettings.serializers import SNSSubscriptionRequestSerializer
from scuba.libs.rest_framework.parsers import AWSJSONParser


class BuildAPI(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SNSSubscriptionRequestSerializer
    parser_classes = [AWSJSONParser]

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        if request.data.get('Type') == 'SubscriptionConfirmation':
            serializer = SNSSubscriptionRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        fh = open("/tmp/build.txt", "a")
        fh.write(json.dumps(request.data) + "\n")
        fh.close()

        return Response(status=200)
