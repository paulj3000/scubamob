from PIL import Image, UnidentifiedImageError

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from scuba.galleries.models import Album, AlbumImage, IMAGE_TYPE_EXTENSIONS, MAX_UPLOAD_SIZE


@login_required
@require_http_methods(["POST"])
def upload(us_request):
    album_id = us_request.POST.get('albumId')
    uploaded_image = us_request.FILES.get('image')

    if not album_id or not uploaded_image:
        return JsonResponse({'error': 'albumId and image are required'}, status=400)

    # ownership check -- only the album's owner may upload to it
    album = get_object_or_404(Album, id=album_id, user=us_request.user)

    if uploaded_image.content_type not in IMAGE_TYPE_EXTENSIONS:
        return JsonResponse({'error': 'unsupported image type'}, status=400)

    if uploaded_image.size > MAX_UPLOAD_SIZE:
        return JsonResponse({'error': 'image is too large'}, status=400)

    try:
        Image.open(uploaded_image).verify()
    except (UnidentifiedImageError, OSError):
        return JsonResponse({'error': 'file is not a valid image'}, status=400)
    finally:
        uploaded_image.seek(0)

    galleries_file = album.add_image(uploaded_image)
    galleries_file_thumbnail = album.add_image_thumbnail(uploaded_image)

    AlbumImage.objects.create(
        album=album,
        image=galleries_file,
        thumbnail=galleries_file_thumbnail)

    retval = {
        'data': {
            'items': [
                {'thumbnail': galleries_file_thumbnail,
                 'full': galleries_file}]
        }
    }

    return JsonResponse(retval)
