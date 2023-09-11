import logging

from django import forms

from scuba.accounts.models import User
from scuba.security.models import BlockedCountry
from scuba.accounts.validators.signup import validate_password
from scuba.settings import IS_PRODUCTION


logger = logging.getLogger(__name__)


class SignupForm(forms.ModelForm):
    """ AccountForm

    Sign up a new user
    """
    is_spam = forms.BooleanField(required=False, widget=forms.HiddenInput(), initial=False)
    ip_address = forms.CharField(widget=forms.HiddenInput(), initial='0.0.0.0')

    class Meta:
        model = User
        fields = ('username',
            'first_name',
            'last_name',
            'date_of_birth','email',
            'password',)

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email', 'unknown@unknown.com')

        # here is the form data submitted
        '''
        message = {
            'form_data': cleaned,
            'is_spam': self.is_spam,
            'iso_country': iso_country,
            'blocked': blocked_name}
        '''

        if IS_PRODUCTION:
            # here is the form data submitted
            blocked, iso_country = BlockedCountry.is_ip_available(getattr(self, 'ip_address'))
            blocked_name = blocked.name if blocked else 'Unknown'

            if blocked:
                InvalidCountry.objects.create(
                    email=email, view=InvalidCountry.VIEW_SIGNUP,
                    ip_address=self.ip_address, iso_country=blocked)

                raise forms.ValidationError("This request cannot be processed")

            setattr(self, 'iso_country', iso_country)

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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user
