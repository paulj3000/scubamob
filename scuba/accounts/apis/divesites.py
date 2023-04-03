import requests
import logging

from rest_framework.response import Response
from rest_framework import generics
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.shortcuts import get_object_or_404

from scuba.accounts.serializers.divesites import UserDivesiteFavoriteSerializer
from scuba.accounts.models import UserEmail, User, UserDivesiteFavorite
from scuba.accounts.exceptions import InvalidEmailIdException, PrimaryEmailIdException
from scuba.sitesettings.models import SettingsApi
from scuba.divesites.models import Divesite


logger = logging.getLogger(__name__)


class UserDivesiteFavoriteList(generics.ListCreateAPIView):
    """ User Divesite Favorite List

    This handles a new email address being added to
    the system
    """
    serializer_class = UserDivesiteFavoriteSerializer

    def get_queryset(self):
        user = self.request.user
        return user.divesites_favorites.all()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'favorites': response.data
       })


class UserDivesiteFavorite(generics.RetrieveDestroyAPIView):
    """ User Divesite Favorite List

    This handles a new email address being added to
    the system
    """
    serializer_class = UserDivesiteFavoriteSerializer
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        id = self.kwargs['id']

        return user.divesites_favorites.filter(id=id)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def xxxpost(self, request, divesiteid):
        divesite = get_object_or_404(Divesite, id=divesiteid)

        user = request.user
        if request.data.get('is_favorite') and \
            request.data['is_favorite'] == 0:
                user.set_divesite_favorite(divesite, false)
                return Response(status=status.HTTP_204_NO_CONTENT)

        user.set_divesite_favorite(divesite)
        return Response(status=status.HTTP_201_CREATED)
