import logging

from django.forms import ModelForm, ValidationError

from scuba.accounts.models import User
from scuba.security.models import BlockedCountry
from scuba.accounts.validators.signup import validate_password
from scuba.settings import IS_PRODUCTION


logger = logging.getLogger(__name__)


class SignupForm(ModelForm):
    """ AccountForm

    Sign up a new user
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'date_of_birth', 'email', 'password',)

    def set_is_spam(self, spam):
        self.is_spam = spam

    def set_ip_address(self, ip_address):
        self.ip_address = ip_address

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email', 'unknown@unknown.com')

        # here is the form data submitted
        #message = {'form_data': cleaned, 'is_spam': self.is_spam, 'iso_country': iso_country, 'blocked': blocked_name}
        #Log.objects.create(system='REGISTER', message=json.dumps(message))

        if hasattr(self, 'is_spam'):
            raise ValidationError("This request cannot be processed")

        if email.endswith('.ru'):
            raise ValidationError("This request cannot be processed")


        if IS_PRODUCTION:
            # here is the form data submitted
            blocked, iso_country = BlockedCountry.is_ip_available(getattr(self, 'ip_address'))
            blocked_name = blocked.name if blocked else 'Unknown'


            if blocked:
                InvalidCountry.objects.create(
                    email=email, view=InvalidCountry.VIEW_SIGNUP,
                    ip_address=self.ip_address, iso_country=blocked)

                raise ValidationError("This request cannot be processed")

            setattr(self, 'iso_country', iso_country)

        # return the cleaned data
        return cleaned

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')

        if full_name.endswith('whofe'):
            raise ValidationError('Cannot register account')

        return full_name

    def clean_password(self):
        """ clean_password

        Validate the password, make sure it fulfils the required
        specifications
        """
        password = self.cleaned_data.get('password')

        if not validate_password(password):
            raise ValidationError(
                'Your password must be between 4 and 20 characters'
            )

        # return the cleaned password
        return password

    def clean_email(self):
        """ clean_email

        Has this email already been registered??
        """
        email = self.cleaned_data.get('email')

        # check to see if this email address has already been used
        if User.objects.filter(email=email):
            raise ValidationError(f"{email} is already registered")

        # return the clenaed password
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user
