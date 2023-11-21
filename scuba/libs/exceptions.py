class InvalidContentTypeException(Exception):
    pass


class InvalidHttpStatusCode(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)

        self.status_code = status_code
        self.message = message


class ChatServerDownException(Exception):
    pass


class InvalidWeatherDataException(Exception):
    """ InvalidWeatherDataException

    Thrown when a key from the weather data API is
    not properly parsed / returned
    """


class InvalidAWSKey(Exception):
    """ InvalidAWSKey

    Thrown when a bad key is sent in
    """
