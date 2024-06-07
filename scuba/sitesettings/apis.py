from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from scuba.sitesettings.models import SystemApi, Endpoint
from scuba.sitesettings.serializers import SystemApiSerializer, SystemEndpointApi


class GetSystemEndpointsApi(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SystemEndpointApi

    def get(self, request):
        data = Endpoint.get_active_endpoints()

        endpoints = self.serializer_class(data, many=True)
        retval = {
            'endpoints': endpoints.data
        }

        return Response(retval)


class GetSystemSettingsApi(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SystemApiSerializer

    def get(self, request):

        if request.META['PATH_INFO'] == '/api/sitesettings/all':
            data = SystemApi.objects.all()
            settings = self.serializer_class(data, many=True).data

            return Response({'settings': settings})

        keys = request.query_params.getlist('key')
        data = SystemApi.objects.filter(key__in=keys)

        retval = {
            'apis': {item.key: item.url for item in data}
        }

        return Response(retval)
