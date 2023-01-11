from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from scuba.home.models import Jumbotron
from scuba.home.serializers import JumbotronSerializer
from scuba.accounts.models import User


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


class SearchApi(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    def get(self, request):

        q_param = request.query_params.get('q')
        users = User.objects.filter(username__icontains=q_param)

        retval = []
        if q_param:
            for user in users:
                retval.append({'id': user.pk_as_str, 'title': user.get_full_name()})

        return Response({'search': retval})
