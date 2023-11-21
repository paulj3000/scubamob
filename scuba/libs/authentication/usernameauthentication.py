from scuba.accounts.models import User
import scuba.settings


class UsernameAuthentication:
    '''
    Authenticate a user based on the legacy login.  Get the login based
    on the phone number
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        # let's see if we can try to find a username or password
        if username is None:
            username = kwargs.get('username')

        if password is None:
            password = kwargs.get('password')

        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                user = None

        # nope, the user does not exist
        except User.DoesNotExist:
            user = None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
