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
        fields = ['url', 'type',]
