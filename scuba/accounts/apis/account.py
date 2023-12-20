from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny

from scuba.accounts.serializers.account import RegisterSerializer, LoginSerializer
from scuba.divesites.serializers import DivesiteReviewSerializer


class RegisterUserApi(generics.CreateAPIView):
    """ Block User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)


class LoginUserApi(generics.GenericAPIView):
    """ Login User

    This class handles the API calls of the password reset functionality
    of the site
    """
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        """ post

        Do the actual posting of the password reset
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetReviewsApi(generics.ListAPIView):
    serializer_class = DivesiteReviewSerializer

    def get_queryset(self):
        user = self.request.user
        return user.reviews.all().order_by('review_date')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'reviews': response.data
        })
