from django.db.models import Q

from rest_framework.response import Response
from rest_framework import generics

from scuba.accounts.models import User
from scuba.accounts.models import UserBlocked, UserBuddy
from scuba.accounts.serializers import profile as serializers


class GetProfileApi(generics.RetrieveAPIView):
    serializer_class = serializers.ProfileSerializer
    lookup_field = 'id'

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())

        instance = args[0]
        user = self.request.user
        if instance != user and not UserBuddy.objects.filter(
            user=instance, buddy=user).count():
            if instance.is_private:
                kwargs['is_private'] = True

        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)
        inner_qs = UserBlocked.objects.filter(buddy=self.request.user)
        user = User.objects.filter(id=id) \
            .exclude(blocked_buddy__in=inner_qs)

        if self.request.user == user:
            return user

        return user


class GetMeProfileApi(generics.GenericAPIView):
    lookup_field = 'username'
    serializer_class = serializers.ProfileSerializer

    def get(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user
        user = self.serializer_class(request.user)
        return Response({'profile': user.data})


class QueryApi(generics.GenericAPIView):
    serializer_class = serializers.QuerySerializer

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({'profile': serializer.data})
