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
from django.utils.translation import gettext as _

from scuba.home.models import Jumbotron
from scuba.libs.fileutils import FileUtils
from scuba.libs.exceptions import InvalidHttpStatusCode
#from skm.libs.aws.s3 import S3


class JumbotronForm(ModelForm):
    """ class HomeJumbotronForm

    Form for the program. This is being overridden because we need to make sure the
    is_active flag is NOT set if there is no program file, cover, or "coming soon"
    is set
    """
    VIDEO_FORMATS = ['mp4']
    IMAGE_FORMATS = ['png', 'jpg', 'gif',]

    upload = forms.FileField(validators=[
        FileExtensionValidator(allowed_extensions=['mp4', 'png', 'jpg', 'gif',])])

    class Meta:
        model = Jumbotron
        fields = '__all__'
        exclude = ('filename', 'jumbotron_type',)

    def clean(self, commit=True):
        m = super().save(commit=False)

        upload = self.cleaned_data['upload']
        name = self.cleaned_data['name']

        #ext = guess_extension(video_file.content_type, video_file.read())
        try:
            upload, jtype = Jumbotron.upload_jumbotron(
                upload.name, upload.content_type, upload.read()
            )

            setattr(self, 'filename', upload)
            setattr(self, 'jtype', jtype)
        except InvalidHttpStatusCode:
            raise forms.ValidationError(
                _('Cannot upload media'),
                params={'value': '42'},
            )

    def save(self, commit=True):
        m = super().save(commit=False)

        m.jumbotron_type = getattr(self, 'jtype')
        m.filename = getattr(self, 'filename')

        if commot:
            m.save()

        return m
