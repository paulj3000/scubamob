from django.shortcuts import get_object_or_404
from django.conf.urls.static import static

from rest_framework import serializers

from scuba.accounts.models import User
from scuba.settings import PROFILE_BLANK_URL


class ProfileSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    buddies_count = serializers.SerializerMethodField()
    username = serializers.CharField()
    profile_image = serializers.SerializerMethodField()

    @staticmethod
    def get_buddies_count(data):
        return data.get_buddies_count()

    @staticmethod
    def get_profile_image(data):
        return data.get_profile_image()

    @staticmethod
    def get_full_name(data):
        return data.get_full_name()

    @staticmethod
    def get_id(data):
        return data.pk_as_str


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
