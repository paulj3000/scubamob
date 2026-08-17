from rest_framework import serializers
from django.urls import reverse

from scuba.settings import AWS_CLOUDFRONT
from scuba.divesites.models import DivesiteReview, DivesiteCheckin
import scuba.divesites.serializers as divesites_serializers


class HomeFeedSerializer(serializers.Serializer):
    """ HomeFeedSerializer

    Renders UserFeed entries (reviews/checkins) belonging to any of the
    current user's buddies for the homepage "friends activity" widget,
    including who did it.
    """
    id = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    item = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_type(data):
        return data.get_instance_type_display().upper()

    @staticmethod
    def get_item(data):
        if data.instance_type == 0:
            obj = DivesiteReview.objects.get(id=data.instance_id)
            return divesites_serializers.DivesiteReviewSerializer(obj, divesite=obj.divesite).data
        elif data.instance_type == 1:
            obj = DivesiteCheckin.objects.get(id=data.instance_id)
            if not obj.is_anonymous:
                return divesites_serializers.DivesiteCheckinSerializer(obj).data

        return None

    @staticmethod
    def get_user(data):
        user = data.user
        return {
            'id': user.pk_as_str,
            'username': user.username,
            'full_name': user.get_full_name(),
            'profile_image': user.get_profile_image(),
            'url': reverse('profile', kwargs={'username': user.username}),
        }


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
