from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

import scuba.accounts.serializers.collections as collections_serializers
from scuba.accounts.models import UserCollection
from scuba.divesites.models import Divesite


class CollectionListCreateApi(generics.ListCreateAPIView):
    """ Get Buddies List

    Return all of the buddies for this particular user
    """
    serializer_class = collections_serializers.CollectionSerializer

    def get_queryset(self):
        user = self.request.user
        return user.collections.all().order_by('name')

    def list(self, request, *args, **kwargs):
        instance = request.GET.get('instance')
        divesite = None
        if instance:
            divesite = get_object_or_404(Divesite, id=instance)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, divesite=divesite)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, divesite=divesite)

        return Response({
            'collections': serializer.data
        })


class AddToCollectionApi(generics.CreateAPIView):
    """ Add to Collection API

    Add an object to a collection
    """
    serializer_class = collections_serializers.CollectionItemSerializer

    def post(self, request, id, *args, **kwargs):
        user = request.user

        collection = get_object_or_404(UserCollection, id=id, user=user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(collection=collection)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
