"""
skm/accounts/forms/signup.py

(C) Copyright 2015-2020, Pjs Midnight Labs.  All rights reserved.

Author: Pauljames "The Juggernaut" Dimitriu

This is the form for the signup stuff
"""
import pytz

from django import forms
from django.forms import ModelForm

from scuba.accounts.models import User, UserSetting
from scuba.accounts.forms.admin import ChangeAccountForm


class ChangeAccountForm(ModelForm):
    """ ChangeAccountForm

    When changing a user, add a couple of extra fields.
    """
    ignore_tracking = forms.BooleanField(label='Ignore Tracking', required=False)
    is_protected = forms.BooleanField(label='Protect from Deletion', required=False)
    is_staff_member = forms.BooleanField(label='Is Staff member', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance:
            instance = self.instance
            self.initial['ignore_tracking'] = instance.get_ignore_tracking()
            self.initial['is_protected'] = instance.get_is_protected()

            if instance.is_admin:
                self.fields['is_staff_member'].initial = True
                self.fields['is_staff_member'].widget.attrs['disabled'] = True
            else:
                self.initial['is_staff_member'] = instance.get_is_staff()

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        """ save

        after saving the user, take into account the extra fields
        above. These are going to be stored in settings
        exists, reset the password and return it

        return the new user
        """
        user = super().save(commit=commit)
        user.set_ignore_tracking(self.cleaned_data['ignore_tracking'])
        user.set_is_protected(self.cleaned_data['is_protected'])

        if user.is_admin:
            user.set_is_staff(True)
        else:
            user.set_is_staff(self.cleaned_data['is_staff_member'])

        return user


class SettingsForm(forms.Form):
    """ ChangeAccountForm

    When changing a user, add a couple of extra fields.
    """
    tzs = [(tzone, tzone) for tzone in pytz.all_timezones]
    timezone = forms.ChoiceField(choices=tzs)

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """ save

        after saving the user, take into account the extra fields
        above. These are going to be stored in settings
        exists, reset the password and return it

        return the new user
        """
        user = super().save(commit=commit)
        user.set_ignore_tracking(self.cleaned_data['ignore_tracking'])
        user.set_is_protected(self.cleaned_data['is_protected'])

        return user
