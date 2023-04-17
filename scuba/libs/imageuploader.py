"""
scuba/libs/imageuploader.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

Image processing library to upload a file to S3, compress, resize,
and all of that good stuff
"""
import time
from io import BytesIO

from PIL import Image

from scuba.libs.constants import CONTENT_TYPES, PROGRAM_IMAGE_FORMAT
from scuba.settings import AWS_S3_BUCKET
from scuba.libs.aws.s3 import S3


class ImageUploader:
    """ Simple class to upload images to S3 """

    # size 250 / 250
    #quality = 80

    @staticmethod
    def compress_upload_image(image_file, path, img_format='png'):
        """ upload_program_image

        Given a program image (as file io), resize the image, compress it,
        give it a name, then upload it to S3
        """
        try:
            img = Image.open(image_file)
            new_image = BytesIO()
            img.thumbnail(PROGRAM_IMAGE_FORMAT['size'], Image.ANTIALIAS)
            img.save(new_image,
                     format=PROGRAM_IMAGE_FORMAT['format'],
                     optimize=True,
                     quality=PROGRAM_IMAGE_FORMAT['quality'])

            ImageUploader.upload_file(image_file, f"{path}/raw", img.format)
            return ImageUploader.upload_file(new_image, path, img_format)
        except IOError:
            raise Exception("cannot create thumbnail for '%s'" % image_file)

    @staticmethod
    def upload_file(image_file, base_path, img_format):
        """ upload_file

        Upload the file to S3. This will take in the format parameter
        and set the appropriate content type
        """

        if img_format.lower() == 'jpeg':
            img_format = 'jpg'

        img_format = img_format.lower()

        # generate the file name
        filename = f"{base_path}/img_{int(time.time())}.{img_format.lower()}"

        header = {
            'ContentType': CONTENT_TYPES[img_format],
        }

        # move the file pointer to the beginning
        image_file.seek(0)
        S3.upload_raw_data(AWS_S3_BUCKET, filename, image_file, **header)

        return filename


    '''
    @staticmethod
    def compress_image(image_file):
        """ add_years_to_today

        add a set number of years to today. Note, this will NOT account for leap years,
        it just updates the date
        """
        img = Image.open(image_file)
        imagefile = BytesIO()
        new_image.save(imagefile, format=img.format, optimize=True, quality=ImageUploader)

        #imagedata = imagefile.getvalue()
        return imagefile

    @staticmethod
    def upload_image(raw_image, resized_image, filename):
        img = Image.open(image_file)
        imagefile = BytesIO()
        new_image = img.resize((width, height), Image.ANTIALIAS)
        new_image.save(imagefile, format=img.format, optimize=True, quality=80)

        #imagedata = imagefile.getvalue()
        return imagefile
    '''
