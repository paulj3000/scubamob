from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.core.cache import cache

from django.db.models import Q
from scuba.home.models import Jumbotron
from scuba.home.serializers import JumbotronSerializer
from scuba.home.serializers import BuddySerializer as SearchBuddySerializer
from scuba.accounts.serializers.buddies import BuddySerializer, BuddyRecentActivity
from scuba.accounts.models import User
from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer
from scuba.libs.weather import Weather
from scuba.maps.models import Region


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
        user = request.user
        q_param = request.query_params.get('q')
        users = User.objects.filter(
            Q(last_name__icontains=q_param) | Q(first_name__icontains=q_param))

        if not user.is_anonymous:
            users = users.filter(~Q(id=user.id))

        retval = {'users': SearchBuddySerializer(users, many=True).data}
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
                if int(lat) == 0 and int(lng) == 0:
                    weather = Weather.get_current_by_postal_code('92107')
                else:
                    weather = Weather.get_current_by_lat_lng(lat, lng)
            else:
                code = data.get('postal_code', data['q'])
                weather = Weather.get_current_by_postal_code(code)
        else:
            weather = Weather.get_current_by_postal_code('92107')
        '''
        weather = Weather.get_current_by_q_param(q_param)
        obj = Region.store_weather_region(weather)
        key = f'weather_{obj.pk_as_str}'
        cache.set(key, weather, 3600)

        return Response({
            'buddies': {
                'count': user.get_buddies_count(),
                'list': BuddySerializer(user.get_all_buddies(), many=True).data,
                'recent_activity': BuddyRecentActivity(buddy_recent_activity, many=True).data,
            },
            # 'weather': WeatherSerializer(weather, many=True).data,
            'weather': weather,
            'divesites': {
                'favorites': user.get_divesite_favorites(),
                'list': DivesiteSerializer(Divesite.get_all_active_divesites(), many=True).data
            }
        })
