# -----------------------------------------------------------------------------
# accounts/services/profile_image.py
#
# Validate, sanitize, and store a user's profile image (avatar).
# -----------------------------------------------------------------------------
import time
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from scuba.accounts.exceptions import InvalidProfileImageException
from scuba.libs.aws.s3 import S3
from scuba.libs.stringutils import StringUtils
from scuba.settings import AWS_S3_BUCKET

# Pillow save-format and file extension for each content type we accept.
# Anything not in this map is rejected outright -- the client-declared
# content type is never trusted beyond this allow-list lookup.
PROFILE_IMAGE_FORMATS = {
    'image/jpeg': ('JPEG', 'jpg'),
    'image/png': ('PNG', 'png'),
    'image/webp': ('WEBP', 'webp'),
}

MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
PROFILE_IMAGE_MAX_DIMENSION = 800


def validate_profile_image(uploaded_image):
    """ validate_profile_image

    Reject anything that isn't a reasonably sized, genuinely decodable
    image of an allowed type before it's ever touched by PIL processing
    or sent to S3.
    """
    if uploaded_image.content_type not in PROFILE_IMAGE_FORMATS:
        raise InvalidProfileImageException('Unsupported image type')

    if uploaded_image.size > MAX_PROFILE_IMAGE_SIZE:
        raise InvalidProfileImageException('Image is too large')

    uploaded_image.seek(0)
    try:
        Image.open(uploaded_image).verify()
    except (UnidentifiedImageError, OSError):
        raise InvalidProfileImageException('File is not a valid image')
    finally:
        uploaded_image.seek(0)


def _prepare_image(uploaded_image, save_format):
    """ _prepare_image

    Decode the upload into a fresh Pillow image, correct its orientation,
    and flatten transparency for formats that can't carry it. Re-encoding
    from decoded pixel data (rather than re-uploading the client's raw
    bytes) means only actual image content is ever persisted -- embedded
    EXIF/GPS data and anything smuggled outside the pixel data is dropped.
    """
    image = Image.open(uploaded_image)
    image = ImageOps.exif_transpose(image)

    if save_format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGBA')
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1])
        image = background
    elif image.mode == 'P':
        image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')

    if max(image.size) > PROFILE_IMAGE_MAX_DIMENSION:
        image.thumbnail((PROFILE_IMAGE_MAX_DIMENSION, PROFILE_IMAGE_MAX_DIMENSION), Image.LANCZOS)

    return image


def set_profile_image(user, uploaded_image):
    """ set_profile_image

    Validate an uploaded avatar, store it in S3 under a server-generated
    key, and update (or create) the user's UserProfileImage record,
    replacing and cleaning up any previous one.
    """
    from scuba.accounts.models import UserProfileImage  # avoid a models<->services import cycle

    validate_profile_image(uploaded_image)

    save_format, ext = PROFILE_IMAGE_FORMATS[uploaded_image.content_type]
    image = _prepare_image(uploaded_image, save_format)

    buffer = BytesIO()
    image.save(buffer, format=save_format)

    sub_name = StringUtils.generate_random_number(8)
    base_name = f"profiles/{user.aws_id}/{sub_name}_{int(time.time())}.{ext}"

    S3.upload_raw_data(
        base_name, buffer.getvalue(), bucket=AWS_S3_BUCKET,
        ContentType=uploaded_image.content_type)

    previous_key = None
    if hasattr(user, 'userprofileimage'):
        profile_image = user.userprofileimage
        previous_key = profile_image.image
        profile_image.image = base_name
        profile_image.save()
    else:
        profile_image = UserProfileImage.objects.create(user=user, image=base_name)

    if previous_key and previous_key != base_name:
        S3.delete_file(previous_key, bucket=AWS_S3_BUCKET)

    return profile_image
