from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.core.cache import cache

from django.db.models import Q
from scuba.home.serializers import BuddySerializer as SearchBuddySerializer
from scuba.accounts.serializers.buddies import BuddySerializer, BuddyRecentActivity
from scuba.accounts.models import User
from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer
from scuba.libs.weather import Weather
from scuba.libs.exceptions import InvalidWeatherDataException
from scuba.maps.models import Region


class SearchApi(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        user = request.user
        q_param = request.query_params.get('q')
        c_param = request.query_params.get('c')

        retval = {}
        if user.is_authenticated:
            if c_param == 'b' or not c_param:
                users = User.objects.filter(
                    Q(last_name__icontains=q_param) | Q(first_name__icontains=q_param)
                ).filter(~Q(id=user.id))
                retval['users'] = SearchBuddySerializer(users, many=True).data

        return Response(retval)


class GetHomescreenApi(generics.GenericAPIView):
    def get(self, request):
        user = request.user
        buddy_recent_activity = user.get_all_buddies_recent_activity()

        q_param = request.query_params.get('q', 92107)

        # cache by query param so repeated requests for the same location
        # skip the external API call entirely -- the cache key can't be
        # derived from the region until *after* a fetch (the region is
        # resolved from the weather response itself), so caching on
        # q_param is what actually makes the cache useful.
        cache_key = f'weather_query_{q_param}'
        weather = cache.get(cache_key)

        if weather is None:
            # check for the weather. If it doesn't return, give the
            # default location of 92107
            try:
                weather = Weather.get_current_by_q_param(q_param)
            except InvalidWeatherDataException:
                weather = Weather.get_current_by_q_param('92107')

            cache.set(cache_key, weather, 3600)

        obj = Region.store_weather_region(weather)

        location = weather.pop('location')
        location['id'] = obj.pk_as_str

        return Response({
            'buddies': {
                'count': user.get_buddies_count(),
                'list': BuddySerializer(user.get_all_buddies(), many=True).data,
                'recent_activity': BuddyRecentActivity(buddy_recent_activity, many=True).data,
            },
            # 'weather': WeatherSerializer(weather, many=True).data,
            'weather': weather.pop('current'),
            'location': location,
            'divesites': {
                'favorites': user.get_divesite_favorites(),
                'list': DivesiteSerializer(Divesite.get_all_active_divesites(),
                                           many=True, type='simple').data
            }
        })
