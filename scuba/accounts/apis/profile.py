from django.http import Http404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework import generics

from scuba.accounts.models import User
from scuba.accounts.models import UserBlocked
from scuba.accounts.serializers.profile import ProfileSerializer


class GetProfileApi(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    lookup_field = 'id'

    def get_queryset(self):
        id = self.kwargs.get(self.lookup_field)
        inner_qs = UserBlocked.objects.filter(buddy=self.request.user)
        user = User.objects.filter(id=id) \
            .filter(is_private=False) \
            .exclude(blocked_buddy__in=inner_qs)

        if self.request.user == user:
            return user

        return user


class GetMeProfileApi(generics.GenericAPIView):
    lookup_field = 'username'
    serializer_class = ProfileSerializer

    def get(self, request):
        """ post

        Do the actual posting of the password reset
        """
        user = request.user
        user = self.serializer_class(request.user)
        return Response({'profile': user.data})
