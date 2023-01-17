from django.contrib import messages

from rest_framework import generics
from rest_framework.response import Response


class AddUIMessageApi(generics.GenericAPIView):
    def post(self, request):
        if request.data.get('message'):
            messages.add_message(request, messages.INFO, request.data['message'])

        return Response()
