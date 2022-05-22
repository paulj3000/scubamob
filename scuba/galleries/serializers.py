from rest_framework import serializers

from scuba.galleries.models import Album, Media
from scuba.settings import AWS_CLOUDFRONT


class AlbumSerializer(serializers.ModelSerializer):
    """ CauseSerializer

    The serializer for a program
    Function takes in a program object and converts it to appropriate
    json objects
    """
    class Meta:
        """ define models, fields, etc """
        model = Album
        fields = '__all__'

    @staticmethod
    def get_url(data):
        return f"{AWS_CLOUDFRONT}/{data.filename}"

    def create(self, validated_data):
        retval = []
        file = validated_data['file']
        return Media.upload_new_media(fileinfo.name, fileinfo.content_type, fileinfo.read())


class MediaSerializer(serializers.Serializer):
    """ CauseSerializer

    The serializer for a program
    Function takes in a program object and converts it to appropriate
    json objects
    """
    file = serializers.FileField(write_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(read_only=True)

    @staticmethod
    def get_url(data):
        return f"{AWS_CLOUDFRONT}/{data.filename}"

    def create(self, validated_data):
        retval = []
        file = validated_data['file']
        return Media.upload_new_media(fileinfo.name, fileinfo.content_type, fileinfo.read())
