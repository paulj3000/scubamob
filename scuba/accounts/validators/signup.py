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


def validate_username(username):
    """ validate_username

    A generic class to validate the username.

    returns a boolean: True if password fulfils the params else
        return false
    """
    if len(password) < 5:
        return False

    # the passord is good. We will return True
    return True
