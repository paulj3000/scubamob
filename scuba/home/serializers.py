from rest_framework import serializers

from scuba.home.models import Jumbotron
from scuba.settings import AWS_CLOUDFRONT


class JumbotronSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    @staticmethod
    def get_url(data):
        return f'{AWS_CLOUDFRONT}{data.filename}'

    @staticmethod
    def get_type(data):
        return 'video' if data.is_video else 'image'

    class Meta:
        """ define models, fields, etc """
        model = Jumbotron
        fields = ['url', 'type']


class BuddySerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_image(data):
        return data.get_profile_image()

    @staticmethod
    def get_full_name(data):
        return data.get_full_name()

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_first_name(data):
        return data.first_name

    @staticmethod
    def get_last_name(data):
        return data.last_name
