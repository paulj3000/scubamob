from rest_framework import serializers

from scuba.galleries.models import Album, Media
from scuba.settings import AWS_CLOUDFRONT


class AlbumSerializer(serializers.ModelSerializer):
    """ AlbumSerializer

    The serializer for a gallery album. Read-only in practice today --
    albums are created directly via Album.objects.create() in the view layer.
    """
    class Meta:
        """ define models, fields, etc """
        model = Album
        exclude = ('user', 'created', 'modified',)


class MediaSerializer(serializers.Serializer):
    """ MediaSerializer

    The serializer for a single uploaded piece of media
    """
    file = serializers.FileField(write_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(read_only=True)

    @staticmethod
    def get_url(data):
        return f"{AWS_CLOUDFRONT}{data.filename}"

    def create(self, validated_data):
        fileinfo = validated_data['file']
        user = self.context['request'].user
        return Media.upload_new_media(user, fileinfo.name, fileinfo.content_type, fileinfo.read())


class DailyImageSerializer(serializers.Serializer):
    """ DailyImageSerializer

    Serializer for the AWSModel-backed DailyImage (filename/url/created),
    not the same shape as MediaSerializer's Media model.
    """
    url = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_user(data):
        return data.user.get_full_name()
