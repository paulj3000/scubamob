"""
skm/music/forms/admin.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

This form is for entering program tracks into the program's form.
"""
from mimetypes import guess_extension

from django import forms
from django.forms import ModelForm
from django.db.models import Max
from django.core.validators import FileExtensionValidator

from scuba.content.models import Image
from scuba.libs.aws.s3 import S3


class ImageForm(ModelForm):
    """ class ImageForm

    Form for the program. This is being overridden because we need to make sure the
    is_active flag is NOT set if there is no program file, cover, or "coming soon"
    is set
    """
    filename = forms.FileField(validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'png'])])

    class Meta:
        model = Image
        fields = '__all__'

    def save(self, commit=True):
        m = super().save(commit=False)

        image = self.cleaned_data['filename']

        m.save()
        id = str(m.id)

        if not isinstance(image, str):
            ext = guess_extension(image.content_type)
            image_filename = f"uploaded_images/img{id}{ext}"
            S3.upload_public_file(image.temporary_file_path(),
                                  image_filename,
                                  ContentType=image.content_type)

            m.filename = image_filename

        m.save()
        return m
