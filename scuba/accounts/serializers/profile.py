from django.shortcuts import get_object_or_404
from rest_framework import serializers

from scuba.accounts.models import User
from scuba.divesites.models import DivesiteReview, DivesiteCheckin
import scuba.divesites.serializers as divesites_serializers


class ProfileSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        if kwargs.pop('is_private', False):
            self.fields.pop("media", None)
            self.fields.pop("buddy_count", None)

        super().__init__(*args, **kwargs)

    id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    buddy_count = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField()
    followers_count = serializers.IntegerField()
    profile_image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    is_private = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

    def get_is_following(self, data):
        user = self.context['request'].user
        if data.id == user.id:
            return True
        else:
            return data.get_is_following(user)

    def get_is_self(self, data):
        user = self.context['request'].user
        return True if data.id == user.id else False

    @staticmethod
    def get_is_private(data):
        return data.is_private

    @staticmethod
    def get_location(data):
        return data.location

    @staticmethod
    def get_username(data):
        return data.username

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
    def get_buddy_count(data):
        return data.buddy_count

    def to_representation(self, instance):
        """ Modify the return data based on what we're sending in

        If we are looking for something "simple", we don't have to return
        most of the files
        """
        user = self.context['request'].user
        # get the original representation
        ret = super().to_representation(instance)

        if not ret['is_private']:
            return ret

        if not user.buddies.filter(buddy_id=ret.get('id')) and user.pk_as_str != ret['id']:
            # the user is private and they're not buddies yet
            ret.pop('buddy_count')
            ret.pop('reviews_count')
            ret.pop('followers_count')
            ret.pop('location')
            ret.pop('is_following')
            ret.pop('is_self')

        return ret


class BlockUserSerializer(serializers.Serializer):
    username = serializers.CharField()

    def get_serializer_context(self):
        return {"user": self.request.user}

    def validate_username(self, username):
        """ validate_plan

        Validate the plan id coming in
        """
        user = self.context['user']

        if user.username == username:
            raise serializers.ValidationError("You cannot block yourself")

        to_block = get_object_or_404(User, username=username)

        if user.is_blocked(to_block):
            raise serializers.ValidationError("User is already blocked")

        setattr(self, 'to_block', to_block)
        return username

    def create(self, validated_data):
        """ A stub for the create method. This does nothing """
        user = self.context['user']
        user.block_buddy(self.to_block)

        return True


class AddBuddySerializer(serializers.Serializer):
    userid = serializers.CharField()

    def validate_userid(self, userid):
        """ validate_plan

        Validate the plan id coming in
        """
        user = self.context['user']

        if user.id == userid:
            raise serializers.ValidationError("You cannot add yourself")

        to_add = get_object_or_404(User, pk=userid)

        if user.is_blocked(to_add):
            raise serializers.ValidationError("Cannot add user")

        if user.is_add_buddy_requested(to_add):
            raise serializers.ValidationError("Cannot add user")

        setattr(self, 'to_add', to_add)
        return userid

    def create(self, validated_data):
        user = self.context['user']
        user.add_buddy_request(self.to_add)

        return True


class CancelBuddyRequestSerializer(serializers.Serializer):
    userid = serializers.CharField()

    def validate_userid(self, userid):
        """ validate_plan

        Validate the plan id coming in
        """
        user = self.context['user']

        if user.id == userid:
            raise serializers.ValidationError("You cannot block yourself")

        to_cancel = get_object_or_404(User, pk=userid)

        setattr(self, 'to_cancel', to_cancel)
        return userid

    def save(self):
        """ A stub for the create method. This does nothing """
        user = self.context['user']
        user.cancel_buddy_request(self.to_cancel)

        return True


class ConfirmBuddyRequestSerializer(serializers.Serializer):
    userid = serializers.CharField()

    def validate_userid(self, userid):
        """ validate_plan

        Validate the plan id coming in
        """
        user = self.context['user']

        if user.id == userid:
            raise serializers.ValidationError("You cannot block yourself")

        buddy_user = get_object_or_404(User, pk=userid)

        setattr(self, 'buddy_user', buddy_user)
        return userid

    def save(self):
        """ A stub for the create method. This does nothing """
        user = self.context['user']
        user.confirm_buddy_request(self.buddy_user)

        return True


class QuerySerializer(serializers.Serializer):
    q = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_q(data):
        return True

    def validate_userid(self, userid):
        """ validate_plan

        Validate the plan id coming in
        """
        user = self.context['user']

        if user.id == userid:
            raise serializers.ValidationError("You cannot block yourself")

        buddy_user = get_object_or_404(User, pk=userid)

        setattr(self, 'buddy_user', buddy_user)
        return userid


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
            return divesites_serializers.DivesiteCheckinSerializer(obj, divesite=obj.divesite).data

        return None

    def get_reactions(self, data):
        user = self.context['request'].user
        id = data.id

        return {
            'flagged': True if user.flags.filter(user_feed_id=id) else False
        }


class FollowProfileSerializer(serializers.Serializer):
    follow = serializers.BooleanField(write_only=True)
    following = serializers.BooleanField(source='follow', read_only=True)

    def save(self, **kwargs):
        """ A stub for the create method. This does nothing """
        profile = kwargs['profile']
        user = kwargs['user']

        validated_data = {**self.validated_data, **kwargs}
        return profile.set_follow_user(user, validated_data['follow'])
