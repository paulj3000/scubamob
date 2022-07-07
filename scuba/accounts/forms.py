from pprint import pprint
from datetime import datetime
import uuid

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import validate_email
from django.contrib.auth.models import User

from scuba.accounts.models import UserFriendRequest, UserFriend, Account


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'home-form-input create-account';
        self.fields['username'].label = 'Username or Email';
        self.fields['password'].widget.attrs['class'] = 'home-form-input create-account';


class AccountForm(UserCreationForm):
    username = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'home-form-input create-account', 'placeholder':'Username'}), required=True)
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'home-form-input create-account', 'placeholder':'Email'}), required=True)
    password1 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'class':'home-form-input create-account', 'placeholder':'Password'}), required=True)
    password2 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'class':'home-form-input create-account', 'placeholder':'Verify Password'}), required=True)
    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'home-form-input create-account-small', 'placeholder':'First Name'}), required=True)
    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'home-form-input create-account-small', 'placeholder':'Last Name'}), required=True)

    class Meta:
        model = User
        fields = ('username', "first_name", "last_name", "email",)
        #exclude = ('password1',)

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")

        # return the cleaned password
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # check to see if this email address has already been used
        if User.objects.filter(email=email):
            raise forms.ValidationError(
                '%s is already registered' % email
            )

        # return the cleaned password
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            Account.objects.create(user=user)

        return user

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
            model = UserFriendRequest
            fields = ['email']

    def save(self, commit=True):
        # before we even think about saving, let's make sure:
        # if the email is registered, this user is not a friend of
        # the current logged in user
        friend = None
        email = self.cleaned_data['email']

        #UserFriendRequest.objects.get(friend=friend, user=self.user)
        for email in self.cleaned_data['email'].split(','):
            # let's get the email and check if it's already in the system
            try:
                # make sure the email address is correct
                validate_email(email)
            except:
                print(f"bad email:  {email}")
                continue

            friend = None
            try:
                friend = User.objects.get(email=email)
            except:
                pass

            # ok, so far a valid email address.  now, let's check for a valid user
            # first, is this this a valid usre with
            if UserFriend.objects.filter(user__email=email, friend=self.user):
                # the user is already a friend.  forget it
                continue

            if UserFriendRequest.objects.filter(user=self.user, email=email):
                # the user has already been requested
                continue

            # if we got down here, we can add the new user
            friend_id = friend.id if friend else 0
            self.email_invites.append(email)
            UserFriendRequest.objects.create(friend=self.user, email=email, user=friend)


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
