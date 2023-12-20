import logging

from rest_framework.response import Response
from rest_framework import generics

from scuba.accounts.serializers.divesites import UserDivesiteFavoriteSerializer


logger = logging.getLogger(__name__)


class UserDivesiteFavoriteListApi(generics.ListCreateAPIView):
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


class UserDivesiteFavoriteApi(generics.RetrieveDestroyAPIView):
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
