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
from scuba.settings import IMAGE_TYPES, VIDEO_TYPES


class JumbotronForm(ModelForm):
    """ class HomeJumbotronForm

    Form for the program. This is being overridden because we need to make sure the
    is_active flag is NOT set if there is no program file, cover, or "coming soon"
    is set
    """
    upload = forms.FileField(validators=[
        FileExtensionValidator(allowed_extensions=IMAGE_TYPES + VIDEO_TYPES)])

    class Meta:
        model = Jumbotron
        exclude = ('filename', 'jumbotron_type',)
        fields = ('name', 'is_active',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['upload'].widget = forms.HiddenInput()
            self.fields['upload'].required = False

    def save(self, commit=True):
        m = super().save(commit=False)

        cleaned_data = self.cleaned_data

        if cleaned_data.get('upload'):
            upload = cleaned_data['upload']
            name = cleaned_data['name']
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

            m.jumbotron_type = getattr(self, 'jtype')
            m.filename = getattr(self, 'filename')

        if commit:
            m.save()

        return m
