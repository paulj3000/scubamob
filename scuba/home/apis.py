from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from scuba.home.models import Jumbotron
from scuba.home.serializers import JumbotronSerializer


class GetJumbotronApi(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = JumbotronSerializer
    def get(self, request):

        return Response({
            'jumbotron': self.serializer_class(Jumbotron.get_active_jumbotron()).data
        })


class GetDailyPicApi(generics.GenericAPIView):
    serializer_class = JumbotronSerializer
    def get(self, request):

        return Response({
            'jumbotron': self.serializer_class(Jumbotron.get_active_jumbotron()).data
        })
