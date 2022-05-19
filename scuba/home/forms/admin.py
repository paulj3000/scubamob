"""
scuba/home/forms/admin.py

(C) Copyright 2015-2022, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

This form is for entering program tracks into the program's form.
"""
from mimetypes import guess_extension

from django import forms
from django.forms import ModelForm
from django.core.validators import FileExtensionValidator

from scuba.home.models import HomeJumbotron
#from skm.libs.aws.s3 import S3


class HomeJumbotronForm(ModelForm):
    """ class HomeJumbotronForm

    Form for the program. This is being overridden because we need to make sure the
    is_active flag is NOT set if there is no program file, cover, or "coming soon"
    is set
    """
    filename = forms.FileField(validators=[
        FileExtensionValidator(allowed_extensions=['mp3'])])

    class Meta:
        model = HomeJumbotron
        fields = '__all__'

    def save(self, commit=True):
        m = super().save(commit=False)

        cover = self.cleaned_data['cover']
        video_file = self.cleaned_data['filename']

        m.save()
        id = str(m.id)

        base = None
        if m.is_video:
            base = 'video'
        elif m.is_image:
            base = 'img'

        ext = guess_extension(video_file.content_type)
        video_filename = f"home/jumbotrons/{base}_{id}{ext}"
        S3.upload_public_file(video_file.temporary_file_path(),
                              video_filename,
                              ContentType=video_file.content_type)

        m.filename = video_filename

        m.save()
        return m
