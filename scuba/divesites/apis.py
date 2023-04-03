import math
from datetime import datetime, timedelta
from pprint import pprint

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import QueryDict

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response


from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer, DivesiteReviewSerializer


class DivesiteListApi(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = DivesiteSerializer

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        lat = self.request.query_params.get('lat', None)
        lng = self.request.query_params.get('long', None)
        distance = self.request.query_params.get('distance', None)

        return Divesites.get_local_divesites(lat, lng, distance)

    def get_queryset(self):
        """ get_queryset

        get all of categories associated to the section
        """
        '''
        radius = int(us_request.GET['radius'])
        lon = float(us_request.GET['lon'])
        lat = float(us_request.GET['lat'])
        '''
        return Divesite.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        retval = {
            'divesites': self.serializer_class(queryset, many=True).data
        }

        return Response(retval)


class DivesiteReviewListApi(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = DivesiteReviewSerializer

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        lat = self.request.query_params.get('lat', None)
        lng = self.request.query_params.get('long', None)
        distance = self.request.query_params.get('distance', None)

        return Divesites.get_local_diveshops(lat, lng, distance)

    def get_queryset(self):
        """ get_queryset

        get all of categories associated to the section
        """
        '''
        radius = int(us_request.GET['radius'])
        lon = float(us_request.GET['lon'])
        lat = float(us_request.GET['lat'])
        '''

        return Divesite.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        retval = {
            'diveshops': self.serializer_class(queryset, many=True).data
        }

        return Response(retval)
