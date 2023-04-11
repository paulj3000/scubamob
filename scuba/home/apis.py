from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.core.cache import cache

from django.db.models import Q
from scuba.home.models import Jumbotron
from scuba.home.serializers import JumbotronSerializer
from scuba.weather.serializers import WeatherSerializer
from scuba.accounts.serializers.buddies import BuddySerializer, BuddyRecentActivity
from scuba.accounts.models import User
from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer
from scuba.sitesettings.models import APIKey
from scuba.weather.libs.weather import Weather as WeatherAPI


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


class GetHomescreenApi(generics.GenericAPIView):
    def get(self, request):
        user = request.user
        buddy_recent_activity = user.get_all_buddies_recent_activity()

        q_param = request.query_params.get('q', 92107)
        '''
        if data.get('q'):
            if ',' in data['q']:
                lat, lng = data['q'].split(',')
                weather = Weather.get_current_by_lat_lng(lat, lng)
            else:
                code = data.get('postal_code', data['q'])
                weather = Weather.get_current_by_postal_code(code)
        else:
            weather = Weather.get_current_by_postal_code('92107')
        '''

        return Response({
            'buddies': {
                'count': user.get_buddies_count(),
                'list': BuddySerializer(user.get_all_buddies(), many=True).data,
                'recent_activity': BuddyRecentActivity(buddy_recent_activity, many=True).data,
            },
            #'weather': WeatherSerializer(weather, many=True).data,
            'weather': WeatherAPI.get_current_by_q_param(q_param),
            'divesites': {
                'favorites': user.get_divesite_favorites(),
                'list': DivesiteSerializer(Divesite.get_all_active_divesites(), many=True).data
            }
        })
