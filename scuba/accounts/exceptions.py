class InvalidUserIdException(Exception):
    """ Invalid user id exception """


class InvalidEmailIdException(Exception):
    """ Invalid email id exception """


class PrimaryEmailIdException(Exception):
    """ Primary email exception """


class EmailInUseException(Exception):
    """ Email in use exception """


class InvalidConfirmationCodeException(Exception):
    """ Invalid confirmation code exception """


class InvalidProfileImageException(Exception):
    """ Invalid profile image exception """


class IsBlockedException(Exception):
    """ User is blocked """
