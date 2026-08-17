from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from scuba.galleries.models import Album, AlbumImage, DailyImage, Media
from scuba.galleries.serializers import AlbumSerializer, MediaSerializer, DailyImageSerializer


class GetDailyPicApi(generics.GenericAPIView):
    serializer_class = MediaSerializer

    def get(self, request):
        img = DailyImage.objects.filter().first()

        if not img:
            return Response({'image': None})

        return Response({'image': DailyImageSerializer(img).data})


class ListAlbumsApi(generics.ListAPIView):
    """ HomeView

    display the home page
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = AlbumSerializer

    def get_queryset(self):
        """ get_queryset

        get all of categories associated to the section
        """
        return self.request.user.albums.all().order_by('title')

    def list(self, request):
        queryset = self.get_queryset()
        retval = {
            'albums': self.serializer_class(queryset, many=True).data
        }

        return Response(retval)


@login_required
@require_http_methods(["POST"])
def json_createalbum(us_request):
    params = us_request.POST

    # convert the response to JSON
    album = Album.objects.create(
        user=us_request.user, title=params['title'],
        description=params.get('description'), )

    json = album.to_json()
    json['url'] = reverse('show_album', kwargs={'album_id': album.pk_as_str})

    return JsonResponse(json)


@login_required
@require_http_methods(["DELETE"])
def json_deletealbum(us_request, album_id):
    album = get_object_or_404(Album, id=album_id, user=us_request.user)
    album.delete()

    return JsonResponse({'deleted': True})


@login_required
@require_http_methods(['GET'])
def json_getalbumimages(us_request, album_id):
    retval = []
    images = AlbumImage.objects.filter(album__id=album_id, album__user=us_request.user)

    for i in images:
        retval.append({'thumbnail': i.get_thumbnail(), 'image': i.get_image()})

    return JsonResponse({'images': retval})


class MediaUploadApi(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MediaSerializer

    def get_queryset(self):
        """ get_queryset

        get all of categories associated to the section
        """
        return Media.objects.all()

    def post(self, request):
        data = [{'file': value} for _, value in request.data.items()]

        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        retval = {
            'media': serializer.data
        }

        return Response(retval)
