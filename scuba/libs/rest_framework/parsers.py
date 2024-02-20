from rest_framework.parsers import JSONParser

class AWSJSONParser(JSONParser):
    media_type = 'text/plain'
