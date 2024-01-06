from rest_framework.response import Response
from rest_framework import generics

from scuba.sitesettings.models import LogbookApi


class GetAllLogbooks(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        user = self.request.user

        logbooks = LogbookApi.get_all_logbooks(user.pk_as_str)
        return Response(logbooks)
