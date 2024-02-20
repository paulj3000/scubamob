from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from django.core.validators import validate_email
from django.contrib.auth.models import User

from scuba.accounts.models import UserBuddyRequest, UserBuddy


class AuthenticationForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField()
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
        'blocked': _("This account is blocked."),
        'cannot_process': _("This request cannot be processed."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def set_ip_address(self, ip_address):
        self.ip_address = ip_address

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        message = {'form_data': self.cleaned_data}
        Log.objects.create(system='LOGIN', message=json.dumps(message))

        blocked, country = BlockedCountry.is_ip_available(getattr(self, 'ip_address'))
        blocked_name = 'Unknown'

        if blocked:
            blocked_name = blocked.name
            InvalidSignup.objects.create(
                email=email,
                view=InvalidSignup.VIEW_LOGIN,
                ip_address=self.ip_address, blocked_country=blocked)

            raise forms.ValidationError("This request cannot be processed", code='cannot_process')

        self.login_country = country

        if email is not None and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'email': email},
                )

            self.confirm_login_allowed(self.user_cache)

        if not self.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """ confirm_login_allowed

        make sure the user can log in. Is the account active, inactive?
        let's find out
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

        if user.is_blocked:
            raise forms.ValidationError(
                self.error_messages['blocked'],
                code='blocked',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class SettingsForm(ModelForm):
    first_name = forms.CharField(label="First Name", required=True)
    last_name = forms.CharField(label="Last Name", required=True)
    email = forms.CharField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class PasswordForm(ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Password (again)", widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ('password', 'password2')

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")

        # return the clenaed password
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class EmailInviteForm(forms.Form):
    email = forms.CharField(label="", widget=forms.TextInput(), required=True)
    email_invites = []

    def get_email_invites(self):
        return self.email_invites

    class Meta:
        model = UserBuddyRequest
        fields = ['email']

    def save(self, commit=True):
        # before we even think about saving, let's make sure:
        # if the email is registered, this user is not a friend of
        # the current logged in user
        friend = None
        email = self.cleaned_data['email']

        for email in self.cleaned_data['email'].split(','):
            # let's get the email and check if it's already in the system
            try:
                # make sure the email address is correct
                validate_email(email)
            except ValidationError:
                print(f"bad email:  {email}")
                continue

            friend = None
            try:
                friend = User.objects.get(email=email)
            except User.DoesNotExist:
                pass

            # ok, so far a valid email address.  now, let's check for a valid user
            # first, is this this a valid usre with
            if UserBuddy.objects.filter(user__email=email, friend=self.user):
                # the user is already a friend.  forget it
                continue

            if UserBuddyRequest.objects.filter(user=self.user, email=email):
                # the user has already been requested
                continue

            # if we got down here, we can add the new user
            friend_id = friend.id if friend else 0
            self.email_invites.append(email)
            UserBuddyRequest.objects.create(friend=self.user, email=email, user=friend)


def validate_password(password):
    """ validate_password

    A generic class to validate the password for a user. The
    password needs to fulfil the password requirements stuff.

    returns a boolean: True if password fulfils the params else
        return false
    """
    if password and len(password) < 4 or len(password) > 20:
        return False

    # the passord is good. We will return True
    return True


class SignupForm(ModelForm):
    """ SignupForm

    Sign up a new user
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password',)

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')

        if full_name.endswith('whofe'):
            raise forms.ValidationError('Cannot register account')

        return full_name
