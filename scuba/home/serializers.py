from rest_framework import serializers

from scuba.settings import AWS_CLOUDFRONT


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
