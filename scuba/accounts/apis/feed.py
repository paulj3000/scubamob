from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import generics

from scuba.accounts.models import User
from scuba.accounts.serializers import feed as serializers


class FlagApi(generics.GenericAPIView):
    """ Get Feed List

    Return the feed of the user
    """
    serializer_class = serializers.FlagSerializer

    def post(self, request, id, *args, **kwargs):
        data = request.data
        data['feed_id'] = id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'flagged': serializer.data})


class GetFeedApi(generics.ListAPIView):
    """ Get Feed List

    Return the feed of the user
    """
    serializer_class = serializers.FeedSerializer
    lookup_field = 'id'

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)
        user = get_object_or_404(User, id=id)
        return user.get_feed()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'feed': response.data
        })
