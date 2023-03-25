import datetime
from dateutil.relativedelta import relativedelta

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

    @staticmethod
    def validate_password(password):
        """ validate password """

        if len(password) < 8:
            raise serializers.ValidationError("Password needs to be longer")

        return password

    def update(self, instance, validated_data):
        """ A stub for the update method. This does nothing """
        user = self.context['request'].user
        user.set_password(instance['password'])

    def create(self, validated_data):
        raise NotImplementedError


class CreateUserSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True)
    token = serializers.SerializerMethodField(read_only=True)
    confirmed = serializers.SerializerMethodField(read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)
    setup_complete = serializers.BooleanField(read_only=True)

    @staticmethod
    def validate_email(email):
        if User.objects.filter(email=email).count():
            raise serializers.ValidationError(f"'{email}' has already registered")
        return email

    @staticmethod
    def validate_password(password):
        # for now, validate the password is at least eight chars
        if len(password) < 8:
            raise serializers.ValidationError("Password must be eight characters")

        return password

    @staticmethod
    def validate_date_of_birth(date_of_birth):
        ''' make sure the user is at least 13 years old.
        COPPA laws will get us
        '''
        THIRTEEN_YEARS = 13

        if relativedelta(datetime.date.today(), date_of_birth).years < THIRTEEN_YEARS:
            raise serializers.ValidationError('user is not 13 years old')
        return date_of_birth

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_profile_image(data):
        return data.profile_image

    @staticmethod
    def get_confirmed(data):
        return data.confirmed

    @staticmethod
    def get_token(data):
        return data.get_api_token()

    def update(self, instance, validated_data):
        """ A stub for the update method. This does nothing """
        raise NotImplementedError

    def create(self, validated_data):
        date_of_birth = validated_data['date_of_birth']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        password = validated_data['password']
        email = validated_data['email']

        return User.create_user(first_name, last_name, email, password, date_of_birth)
