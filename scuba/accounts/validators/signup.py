from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError

MAX_PASSWORD_LENGTH = 20


def validate_password(password):
    """ validate_password

    Validate a candidate password against this project's maximum length and
    Django's configured AUTH_PASSWORD_VALIDATORS (minimum length, common
    password, fully-numeric, and user-attribute-similarity checks).

    Raises django.core.exceptions.ValidationError, with the specific
    reason(s), if the password is invalid.
    """
    if not password:
        raise ValidationError('Password is required.')

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValidationError(
            f'Password must be no more than {MAX_PASSWORD_LENGTH} characters.')

    django_validate_password(password)


def validate_username(username):
    """ validate_username

    A generic class to validate the username.

    returns a boolean: True if username fulfils the size requirements
        return false
    """
    if len(username) < 5 or len(username) > 20:
        return False

    # the passord is good. We will return True
    return True
