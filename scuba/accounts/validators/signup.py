def validate_password(password):
    """ validate_password

    A generic class to validate the password for a user.

    returns a boolean: True if password fulfils the size requirements else
        return false
    """
    if password and len(password) < 4 or len(password) > 20:
        return False

    # the passord is good. We will return True
    return True


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
