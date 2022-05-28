from rest_framework import serializers

from scuba.divesites.models import Divesite
from scuba.settings import AWS_CLOUDFRONT


class DivesiteSerializer(serializers.ModelSerializer):
    """ CauseSerializer

    The serializer for a program
    Function takes in a program object and converts it to appropriate
    json objects
    """
    class Meta:
        """ define models, fields, etc """
        model = Divesite
        fields = '__all__'

    def create(self, validated_data):
        retval = []
        file = validated_data['file']
        return Media.upload_new_media(fileinfo.name, fileinfo.content_type, fileinfo.read())

