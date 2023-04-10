from rest_framework import serializers

from scuba.divesites.models import Divesite, DivesiteReview


class DivesiteSerializer(serializers.ModelSerializer):
    """ CauseSerializer

    The serializer for a program
    Function takes in a program object and converts it to appropriate
    json objects
    """
    id = serializers.SerializerMethodField()
    difficulty_display = serializers.SerializerMethodField(read_only=True)
    banner = serializers.SerializerMethodField(read_only=True)
    lat = serializers.SerializerMethodField(read_only=True)
    long = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_banner(data):
        return data.banner

    @staticmethod
    def get_lat(data):
        return float(data.lat)

    @staticmethod
    def get_long(data):
        return float(data.long)

    @staticmethod
    def get_difficulty_display(data):
        return data.get_difficulty_display()

    class Meta:
        """ define models, fields, etc """
        model = Divesite
        fields = (
            'id', 'name', 'description', 'lat', 'long', 'difficulty',
            'difficulty_display', 'banner',
        )

    def create(self, validated_data):
        retval = []
        file = validated_data['file']
        return Media.upload_new_media(fileinfo.name, fileinfo.content_type, fileinfo.read())


class DivesiteReviewSerializer(serializers.ModelSerializer):
    """ CauseSerializer

    The serializer for a program
    Function takes in a program object and converts it to appropriate
    json objects
    """
    class Meta:
        """ define models, fields, etc """
        model = DivesiteReview
        fields = '__all__'

    def create(self, validated_data):
        retval = []
        file = validated_data['file']
        return Media.upload_new_media(fileinfo.name, fileinfo.content_type, fileinfo.read())
