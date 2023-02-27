from django.shortcuts import get_object_or_404
from django.conf.urls.static import static
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from rest_framework import serializers

from scuba.accounts.models import User
from scuba.settings import PROFILE_BLANK_URL


class SetUsernameSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, username):
        """ validate_plan

        Validate the plan id coming in
        """
        if User.objects.filter(username=username).count():
            raise serializers.ValidationError(f"Username {username} is already registered")

        return username

    def update(self, instance, validated_data):
        """ A stub for the update method. This does nothing """
        user = self.context['request'].user
        user.username = instance['username']
        user.save()


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()

    def xvalidate_password(self, password):
        """ validate_plan

        Validate the plan id coming in
        """

        if User.objects.filter(username=username).count():
            raise serializers.ValidationError(f"Username {username} is already registered")

        return username

    def update(self, instance, validated_data):
        """ A stub for the update method. This does nothing """
        user = self.context['request'].user
        user.set_password(instance['password'])

    def create(self, validated_data):
        raise NotImplementedError
