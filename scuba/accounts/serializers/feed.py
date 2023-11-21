from rest_framework import serializers

from scuba.divesites.models import DivesiteReview, DivesiteCheckin
from scuba.accounts.models import UserFeedFlagged, UserFeed
import scuba.divesites.serializers as divesites_serializers


class FlagSerializer(serializers.ModelSerializer):
    is_flagged = serializers.BooleanField(default=True)
    feed_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = UserFeedFlagged
        fields = ('is_flagged', 'feed_id',)

    def validate_feed_id(self, feed_id):
        if not UserFeed.objects.filter(id=feed_id):
            raise serializers.ValidationError(f"{feed_id} is not valid")

        return feed_id

    def create(self, validated_data):
        user = self.context['request'].user
        feed_id = validated_data['feed_id']
        is_flagged = validated_data.get('is_flagged', True)

        obj, _ = UserFeedFlagged.objects.update_or_create(user=user, user_feed_id=feed_id,
                                                          defaults={'is_flagged': is_flagged})

        return obj


class FeedSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    item = serializers.SerializerMethodField(read_only=True)
    reactions = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        ''' remove "reactions" if the current user is the feed user '''
        user = kwargs['context']['request'].user
        if (args[0].first() and args[0].first().user == user):
            self.fields.pop("reactions", None)

        super().__init__(*args, **kwargs)

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

    def get_reactions(self, data):
        user = self.context['request'].user
        id = data.id

        return {
            'flagged': True if user.flags.filter(user_feed_id=id) else False
        }
