from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from scuba.divesites.models import Divesite, DivesiteCheckinThank, DivesiteCheckin, DivesiteReview
from scuba.divesites.serializers import DivesiteSerializer, \
    DivesiteReviewSerializer, DivesiteFavoriteSerializer, \
    DivesiteCheckinSerializer, DivesiteCheckinThankSerializer


class GetDivesiteApi(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = DivesiteSerializer

    def get(self, request, id, *args, **kwargs):
        divesite = get_object_or_404(Divesite, id=id)

        serializer = self.get_serializer(divesite)
        return Response({'divesite': serializer.data})


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


class CheckinApi(generics.ListCreateAPIView):
    serializer_class = DivesiteCheckinSerializer

    def get_queryset(self):
        id = self.kwargs['id']
        return DivesiteCheckin.objects.filter(divesite_id=id)

    def post(self, request, id, *args, **kwargs):
        data = request.data
        data['divesite_id'] = id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, **kwargs):
        queryset = self.get_queryset()
        retval = {
            'checkins': self.serializer_class(queryset, many=True).data
        }

        return Response(retval)


class ReviewsApi(generics.ListCreateAPIView):
    serializer_class = DivesiteReviewSerializer

    def get_queryset(self):
        id = self.kwargs['id']
        return DivesiteReview.objects.filter(divesite_id=id)

    def post(self, request, id, *args, **kwargs):
        divesite = get_object_or_404(Divesite, id=id)

        serializer = self.get_serializer(divesite=divesite, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, **kwargs):
        queryset = self.get_queryset()
        retval = {
            'reviews': self.serializer_class(queryset, many=True).data
        }

        return Response(retval)


class FavoriteApi(generics.GenericAPIView):
    """ Favorite Divesite

    Indicate if a divesite is a favorite Divesite
    """
    serializer_class = DivesiteFavoriteSerializer

    def post(self, request, id, *args, **kwargs):
        divesite = get_object_or_404(Divesite, id=id)

        serializer = self.get_serializer(divesite=divesite, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class CheckinThankApi(generics.GenericAPIView):
    """ Thank the divesite

    Indicate if a divesite is a favorite Divesite
    """
    serializer_class = DivesiteCheckinThankSerializer

    def post(self, request, id, *args, **kwargs):
        checkin = get_object_or_404(DivesiteCheckin, id=id)

        serializer = self.get_serializer(divesite_checkin=checkin, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class FavoriteListApi(generics.ListAPIView):
    serializer_class = DivesiteSerializer

    def get_queryset(self):
        user = self.request.user
        return Divesite.objects.filter(followers__user=user)

    def list(self, request):
        queryset = self.get_queryset()
        retval = {
            'favorites': self.serializer_class(queryset, many=True).data
        }

        return Response(retval)
