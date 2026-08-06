from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from scuba.accounts.models import User
from scuba.accounts.serializers import profile as serializers
from scuba.accounts.serializers import buddies as buddies_serializers
from scuba.galleries import serializers as galleries_serializers
from scuba.accounts.models import ViewProfile, UserBlocked
from scuba.accounts.exceptions import IsBlockedException
from scuba.accounts.permissions import CanViewProfile
from scuba.divesites.models import DivesiteCheckin
from scuba.divesites.serializers import DivesiteCheckinSerializer


def get_profile(user, profile_id):
    profile = get_object_or_404(User, id=profile_id)
    blocked = UserBlocked.objects.filter(Q(buddy_id=profile_id, user=user) |
                                         Q(user=user, buddy_id=profile_id))

    if blocked:
        raise IsBlockedException

    return profile


class GetProfileApi(generics.RetrieveAPIView):
    serializer_class = serializers.ProfileSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated & CanViewProfile]

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)
        return ViewProfile.objects.filter(id=id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'profile': serializer.data})


class GetMeProfileApi(generics.GenericAPIView):
    serializer_class = serializers.ProfileSerializer

    def get(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user
        profile = ViewProfile.objects.get(id=user.id)
        user = self.serializer_class(profile, context=self.get_serializer_context())
        return Response({'profile': user.data})


class GetGalleryApi(generics.ListAPIView):
    serializer_class = galleries_serializers.MediaSerializer
    permission_classes = [IsAuthenticated & CanViewProfile]
    lookup_field = 'id'

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)
        user = get_object_or_404(User, id=id)
        return user.media

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'media': response.data
        })


class GetCheckinsApi(generics.ListAPIView):
    serializer_class = DivesiteCheckinSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        return DivesiteCheckin.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'checkins': response.data
        })


class GetAlbumsApi(generics.ListAPIView):
    serializer_class = galleries_serializers.AlbumSerializer
    permission_classes = [IsAuthenticated & CanViewProfile]
    lookup_field = 'id'

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'albums': response.data
        })

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)
        user = get_object_or_404(User, id=id)
        return user.albums


class GetPhotosApi(generics.ListAPIView):
    serializer_class = galleries_serializers.MediaSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return self.request.user.get_photos()


class QueryApi(generics.GenericAPIView):
    serializer_class = serializers.QuerySerializer

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({'profile': serializer.data})


class GetBuddiesListApi(generics.ListAPIView):
    """ Get Buddies List

    Return all of the buddies for this particular user
    """
    serializer_class = buddies_serializers.BuddySerializer
    permission_classes = [IsAuthenticated & CanViewProfile]
    lookup_field = 'id'

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)
        user = get_object_or_404(User, id=id)
        return user.get_all_buddies()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'buddies': response.data
        })


class GetFeedApi(generics.ListAPIView):
    """ Get Feed List

    Return the feed of the user
    """
    serializer_class = serializers.FeedSerializer
    permission_classes = [IsAuthenticated & CanViewProfile]
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


class FollowProfileApi(generics.GenericAPIView):
    """ FollowProfileApi

    Return the feed of the user
    """
    serializer_class = serializers.FollowProfileSerializer
    permission_classes = [IsAuthenticated & CanViewProfile]

    def post(self, request, id):

        profile = get_profile(request.user, id)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, profile=profile)

        # response
        return Response(serializer.data)
