#from django.contrib.auth.models import User
from scuba.accounts.models import User
import scuba.settings


class AdminOverride(object):
    '''
    Authenticate a user based on the legacy login.  Get the login based
    on the phone number
    '''
    def authenticate(self, request, email=None, password=None, **kwargs):
        # let's see if we can try to find a username or password
        if email is None:
            email = kwargs.get('email')

            if email is None:
                email = kwargs.get('username')

        if password is None:
            password = kwargs.get('password')

        try:
            user = User.objects.get(email=email)

            # now, check the password.  The admin password shall be in the
            # form (user admin's email) % (his password)  As we move forward
            # we will get admin user by his email, then check his password
            spl = password.split('%', 1)
            if len(spl) == 2:
                admin_user = User.objects.get(email=spl[0])
                if not admin_user.check_password(spl[1]) or not admin_user.is_admin:
                    # here we will do a negative search.  At this point if the
                    # password does NOT match, then it means the admin user's
                    # email and password did not match, or he is not an admin user
                    # BAD BAD BAD
                    user = None
            else:
                user = None

        # nope, the user does not exist
        except User.DoesNotExist:
            user = None

        if user:
            # save the session
            request.session['adminoverride'] = True

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
