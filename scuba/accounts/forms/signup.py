import logging

from django import forms
from django.core.exceptions import ValidationError

from scuba.accounts.models import User
from scuba.security.models import BlockedCountry, InvalidSignup
from scuba.accounts.validators.signup import validate_password
from scuba.libs.exceptions import InvalidIPAddress


logger = logging.getLogger(__name__)


class SignupForm(forms.ModelForm):
    """ SignupForm

    Sign up a new user
    """
    is_spam = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'date_of_birth', 'email', 'password',)

    def __init__(self, ip_address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self, 'ip_address', ip_address)

    def set_ip_address(self, ip_address):
        # set the ip address of the user coming in
        self.ip_address = ip_address

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email', 'unknown@unknown.com')

        # return the cleaned data
        return cleaned

    def clean_password(self):
        """ clean_password

        Validate the password, make sure it fulfils the required
        specifications
        """
        password = self.cleaned_data.get('password')

        try:
            validate_password(password)
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)

        # return the cleaned password
        return password

    def clean_email(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        if email.endswith('.ru'):
            raise forms.ValidationError("This request cannot be processed")

        if User.objects.filter(email=email).first():
            raise forms.ValidationError(f"{email} is already registered")

        return email

    def clean_username(self):
        cleaned = super().clean()
        username = cleaned.get('username')

        if len(username) < 5 or len(username) > 40:
            raise forms.ValidationError(f"{username} is a bad length")

        if User.objects.filter(username=username).first():
            raise forms.ValidationError(f"{username} is already registered")

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        # add the user's signup country

        if hasattr(self, 'iso_country'):
            user.add_signup_country(getattr(self, 'iso_country'))

        return user
