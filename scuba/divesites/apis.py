from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer, \
    DivesiteReviewSerializer, DivesiteFollowingSerializer


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


class AddReviewApi(generics.GenericAPIView):
    """ Add Review API

    Add or remove an API
    """
    serializer_class = DivesiteReviewSerializer

    def post(self, request, id, *args, **kwargs):
        divesite = get_object_or_404(Divesite, id=id)

        serializer = self.get_serializer(divesite=divesite, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowingApi(generics.GenericAPIView):
    """ Block User

    Block a particular user
    """
    serializer_class = DivesiteFollowingSerializer

    def post(self, request, id, *args, **kwargs):
        divesite = get_object_or_404(Divesite, id=id)

        serializer = self.get_serializer(divesite=divesite, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)
