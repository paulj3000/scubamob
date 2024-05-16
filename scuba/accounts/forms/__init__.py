from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm
from django.core.validators import validate_email
from django.contrib.auth.models import User

from scuba.accounts.models import UserBuddyRequest, UserBuddy


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
