from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django.core.cache import cache

from django.db.models import Q
from scuba.home.models import Jumbotron
from scuba.home.serializers import JumbotronSerializer
from scuba.accounts.serializers.buddies import BuddySerializer, BuddyRecentActivity
from scuba.accounts.models import User
from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer
from scuba.weather.models import Weather


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
        users = User.objects.filter(Q(last_name__icontains=q_param) |
                                    Q(first_name__icontains=q_param))

        retval = []
        if q_param:
            for user in users:
                retval.append({'id': user.pk_as_str, 'title': user.get_full_name()})

        return Response({'search': retval})


class GetWeatherFromZip(generics.GenericAPIView):
    serializer_class = JumbotronSerializer

    def get(self, request):
        return Response({
            'jumbotron': 'x'
        })


class GetHomescreenApi(generics.GenericAPIView):
    def get(self, request):
        user = request.user

        data = request.data
        dist = data.get('distance', 100)
        if data.get('lat') and data.get('long'):
            lat = data['lat']
            long = data['long']
            weather = Weather.get_current_by_lat_long(lat, long)[0]

        else:
            code = data.get('postal_code', 92107)
            weather = Weather.get_current_by_postal_code(code)[0]

        return Response({
            'buddies': {
                    'count': user.get_buddies_count(),
                    'list': BuddySerializer(user.get_all_buddies(), many=True).data,
                    'recent_activity': BuddyRecentActivity(user.get_all_buddies_recent_activity(), many=True).data,
                },
                'weather': weather.data,
                'divesites': {
                    'favorites': user.get_divesite_favorites(),
                    'list': DivesiteSerializer(Divesite.get_all_active_divesites(), many=True).data
                }
            })
