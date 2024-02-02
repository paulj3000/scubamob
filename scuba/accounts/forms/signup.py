import logging

from django import forms

from scuba.accounts.models import User
from scuba.security.models import BlockedCountry, InvalidCountry
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

        # check if the ip address is from an invalid country. If it is, return an error
        ip_address = getattr(self, 'ip_address', None)

        if ip_address:
            try:
                blocked_data = BlockedCountry.is_ip_from_blocked_country(ip_address)
                if blocked_data[0]:
                    InvalidCountry.objects.create(
                        email=email, view=InvalidCountry.VIEW_SIGNUP,
                        ip_address=self.ip_address, blocked_country=blocked_data[0])

                    logger.info(f"{ip_address}: Request came from country {blocked_data[1]}")
                    raise forms.ValidationError("This request cannot be processed")

                setattr(self, 'iso_country', blocked_data[1])

            except InvalidIPAddress:
                # the IP address is not valid
                logger.info(f"{ip_address}: No data was returned")
                raise forms.ValidationError("This request cannot be processed")

        # return the cleaned data
        return cleaned

    def clean_password(self):
        """ clean_password

        Validate the password, make sure it fulfils the required
        specifications
        """
        password = self.cleaned_data.get('password')

        if not validate_password(password):
            raise forms.ValidationError(
                'Your password must be between 4 and 20 characters'
            )

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
