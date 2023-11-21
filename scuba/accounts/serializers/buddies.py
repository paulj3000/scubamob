from django.shortcuts import get_object_or_404
from django.conf.urls.static import static
from django.http import Http404
from django.urls import reverse

from rest_framework import serializers

from scuba.accounts.models import User, UserRecentActivity


class BlockUserSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        buddy = kwargs.pop('buddy', None)
        setattr(self, 'buddy', buddy)
        super().__init__(*args, **kwargs)

    def validate_buddy_id(self, buddy_id):
        """ validate_buddy_id

        Verify the buddy id coming in is not the current user, already
        blocked, etc.
        """
        user = self.context['request'].user

        buddy = User.objects.filter(id=buddy_id).first()
        if not buddy:
            raise serializers.ValidationError(f"{buddy_id} cannot be blocked")

        if user.pk_as_str == buddy.pk_as_str:
            raise serializers.ValidationError("You cannot block yourself")

        if user.is_blocked(buddy):
            raise serializers.ValidationError("User is already blocked")

        setattr(self, 'to_block', buddy)
        return buddy_id

    def save(self):
        """ A stub for the create method. This does nothing """
        user = self.context['request'].user
        buddy = getattr(self, 'buddy')

        if user.pk_as_str == buddy.pk_as_str:
            raise serializers.ValidationError("You cannot block yourself")

        user.remove_buddy(buddy)
        return user.block_buddy(buddy)

    def update(self, instance, validated_data):
        """ update

        Not implemented
        """
        raise NotImplementedError


class FollowBuddySerializer(serializers.Serializer):
    follow = serializers.BooleanField(default=True)

    def create(self, validated_data):
        """ A stub for the create method. This does nothing """
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ set the buddy's follow flag correctly """
        user = self.context['request'].user
        instance.set_follow(validated_data['follow'])
        return instance


class AddBuddySerializer(serializers.Serializer):
    buddy_id = serializers.CharField()

    def validate_buddy_id(self, buddy_id):
        """ validate_buddy_id

        Validate buddy id coming in, make sure it's a
        legitimate user
        """
        user = self.context['request'].user

        if user.pk_as_str == buddy_id:
            raise serializers.ValidationError("You cannot add yourself")

        to_add = User.objects.filter(pk=buddy_id).first()
        if not to_add:
            raise serializers.ValidationError("Cannot add buddy")

        # is the user blocked??
        if user.is_blocked(to_add) or to_add.is_private:
            raise Http404

        # is there already a user request for this?
        if user.is_add_buddy_requested(to_add):
            raise serializers.ValidationError("Cannot add buddy")

        setattr(self, 'buddy', to_add)
        return buddy_id

    def create(self, validated_data):
        """ create

        Create the buddy request
        """
        user = self.context['request'].user
        buddy = getattr(self, 'buddy')

        return user.add_buddy_request(buddy)


class AcceptBuddyRequestSerializer(serializers.Serializer):
    id = serializers.CharField(write_only=True)
    buddy = serializers.SerializerMethodField()

    @staticmethod
    def get_buddy(data):
        return BuddySerializer(data).data

    def validate_id(self, request_id):
        """ validate_id

        Validate the buddy request coming in
        """
        user = self.context['request'].user
        request = user.buddy_requested.filter(id=request_id).first()

        if not request or not request.is_active:
            raise serializers.ValidationError(f"{request_id} is not a valid request")

        if user.is_blocked(request.user):
            raise serializers.ValidationError(f"{request_id} is no longer valid")

        setattr(self, 'request', request)
        return request_id

    def create(self, validated_data):
        """ create

        Create the buddy object and set the request

        VERY important. This is the USER accepting the BUDDY's request,
        not the other way around.
        """
        request = getattr(self, 'request')
        request.accept_request()

        # remember, the current user is the "buddy" being accepted
        user = self.context['request'].user
        buddy = request.user

        # add the buddy
        return user.add_buddy(buddy)

    def update(self, instance, validated_data):
        """ update

        Not implemented
        """
        raise NotImplementedError


class BuddySerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_image(data):
        return data.buddy.get_profile_image()

    @staticmethod
    def get_username(data):
        return data.buddy.username

    @staticmethod
    def get_url(data):
        return reverse('profile', kwargs={'username': data.buddy.username})

    @staticmethod
    def get_full_name(data):
        return data.buddy.get_full_name()

    @staticmethod
    def get_first_name(data):
        return data.buddy.first_name

    @staticmethod
    def get_last_name(data):
        return data.buddy.last_name

    @staticmethod
    def get_id(data):
        return data.buddy.pk_as_str

    def create(self, validated_data):
        """ create

        Not implemented
        """
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ update

        Not implemented
        """
        raise NotImplementedError


class BuddyRecentActivity(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = UserRecentActivity
        fields = ('id', 'activity_date',)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    def create(self, validated_data):
        """ create

        Create a new user and all around good stuff here
        """
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ update

        Create a new user and all around good stuff here
        """
        raise NotImplementedError


class RemoveBuddySerializer(serializers.Serializer):
    buddy_id = serializers.CharField()

    def validate_buddy_id(self, buddy_id):
        """ validate_buddy_id

        Verify the buddy id coming in is not the current user, removed,
        blocked, etc.
        """
        user = self.context['request'].user
        buddy = User.objects.filter(id=buddy_id).first()

        if not buddy:
            raise serializers.ValidationError(f"{buddy_id} cannot be removed")

        if user.pk_as_str == buddy.pk_as_str:
            raise serializers.ValidationError("You cannot remove yourself")

        if not user.buddies.filter(buddy_id=buddy_id).first():
            raise serializers.ValidationError(f"{buddy_id} cannot be removed")

        setattr(self, 'to_remove', buddy)
        return buddy_id

    def create(self, validated_data):
        # remove the buddy
        user = self.context['request'].user
        buddy = getattr(self, 'to_remove')

        user.remove_buddy(buddy)
        return user.removed.create(buddy=buddy)

    def update(self, instance, validated_data):
        """ update

        Not implemented
        """
        raise NotImplementedError
