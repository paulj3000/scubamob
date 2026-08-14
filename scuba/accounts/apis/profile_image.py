import logging

from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser

from scuba.accounts.exceptions import InvalidProfileImageException
from scuba.accounts.services import profile_image


logger = logging.getLogger(__name__)


class ProfileImageApi(generics.GenericAPIView):
    """ ProfileImageApi

    Upload (or replace) the current user's profile image / avatar.
    """
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        uploaded_image = request.FILES.get('image')

        if not uploaded_image:
            return Response({'errors': 'image is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            image = profile_image.set_profile_image(request.user, uploaded_image)
        except InvalidProfileImageException as exc:
            return Response({'errors': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'profile_image': image.get_profile_image()})
