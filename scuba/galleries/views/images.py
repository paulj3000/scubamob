from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from scuba.galleries.models import AlbumImage


IMAGE_TYPE_EXTENSIONS = {
    'image/gif': 'gif',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/tiff': 'tiff'
}


@login_required
@require_http_methods(["POST"])
def upload(us_request):
    params = us_request.REQUEST

    account = us_request.user.get_account()

    retval = {'data': {'items': []}}

    # convert the response to JSON
    album_id = params['albumId']
    uploaded_image = us_request.FILES['image']

    # let's get the album
    album = us_request.user.get_album_by_guid(album_id)
    galleries_file = album.add_image(uploaded_image)
    galleries_file_thumbnail = album.add_image_thumbnail(uploaded_image)

    retval['data']['items'] = [
        {'thumbnail': galleries_file_thumbnail,
         'full': galleries_file}]

    AlbumImage.objects.create(
        album=album,
        image=galleries_file,
        thumbnail=galleries_file_thumbnail)

    return JsonResponse(api_response(**retval))
