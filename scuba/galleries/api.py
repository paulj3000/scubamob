from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from scuba.galleries.models import Album, AlbumImage, DailyImage
from scuba.galleries.serializers import AlbumSerializer, MediaSerializer, DailyImageSerializer


class GetDailyPicApi(generics.GenericAPIView):
    serializer_class = MediaSerializer

    def get(self, request):
        img = DailyImage.objects.filter().first()
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
@require_http_methods(["GET"])
def showalbum(us_request, id):
    retval = []

    for album in us_request.user.albums.all():
        json = album.to_json()
        retval.append(json)

    return JsonResponse({'albums': retval})


@login_required
@require_http_methods(["POST"])
def json_createalbum(us_request):
    params = us_request.REQUEST

    retval = []

    try:
        # convert the response to JSON
        album = Album.objects.create(
                    user=us_request.user, title=params['title'],
                    description=params.get('description'), )

        json = album.to_json()
        json['url'] = reverse('show_album', kwargs={'album_id': album.guid})

        return JsonResponse(json)
    except:
        pass


@login_required
@require_http_methods(["GET"])
def getalbums(us_request):
    retval = []
    for album in us_request.user.albums.filter():
        json = album.to_json()
        json['url'] = reverse('show_album', kwargs={'album_id': album.guid})

        try:
            json['cover'] = album.album_image.all().first().thumbnail
        except:
            pass

        img_count = album.album_image.all().count()
        json['image_count'] = "%i %s" % (img_count, 'photo' if img_count == 1 else 'photos')
        retval.append(json)

    return JsonResponse({'albums': retval})


@login_required
@require_http_methods(["DELETE"])
def json_deletealbum(us_request, album_id):
    params = us_request.REQUEST

    retval = []
    # convert the response to JSON
    album = Album.objects.filter(guid=album_id, user=us_request.user).delete()

    return JsonResponse(retval)


@login_required
@require_http_methods(['GET'])
def json_getalbumimages(us_request, album_id):
    params = us_request.REQUEST

    #PRODUCTION_GALLERY_URL
    retval = []
    # convert the response to JSON
    print(f"album id:  {album_id}")
    images = AlbumImage.objects.filter(album__guid=album_id, album__user=us_request.user)

    for i in images:
        retval.append({'thumbnail': i.get_thumbnail(), 'image': i.get_image()})

    return JsonResponse(api_response(data={'items': retval, 'total': len(retval)}))


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

        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        retval = {
            'media': serializer.data
        }

        return Response(retval)
