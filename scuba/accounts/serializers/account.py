from django.shortcuts import get_object_or_404
from django.conf.urls.static import static
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from rest_framework import serializers

from scuba.accounts.models import User
from scuba.settings import PROFILE_BLANK_URL


class RegisterUserSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    username = serializers.CharField()
    token = serializers.SerializerMethodField(read_only=True)
    profile_image = serializers.CharField(read_only=True)

    @staticmethod
    def get_token(data):
        return data.get_api_token()

    def validate_username(self, username):
        """ validate_plan

        Validate the plan id coming in
        """
        if User.objects.filter(username=username).count():
            raise serializers.ValidationError(f"Username {username} is already registered")

        return username

    def validate_email(self, email):
        """ validate_plan

        Validate the plan id coming in
        """
        if User.objects.filter(email=email).count():
            raise serializers.ValidationError(f"Email address {email} is already registered")

        return email


    def create(self, validated_data):
        user = User.objects.create(username=validated_data['username'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'])

        user.set_password(validated_data['password'])
        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    AuthTokenSerializer

    This class handles the validation of the user from way of the API,
    records all login instances and returns
    """
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    device = serializers.CharField(default='mobile', help_text="The device type and build")

    def validate(self, attrs):
        """ validate

        validate the data coming in. Make sure the user can authenticate, then
        return it.
        Raises: validation exception if the user has cannot authenticate
        """
        username = attrs.get('username')
        password = attrs.get('password')
        device = attrs.get('device')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" or "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        """ A stub for the create method. This does nothing """
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ A stub for the update method. This does nothing """
        raise NotImplementedError


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(required=False, read_only=True)
    profile_image = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
    )

    @staticmethod
    def validate_full_name(full_name):
        """ validate_full_name

        make sure the name coming is at least eight characters long
        """
        if len(full_name) < 8:
            raise serializers.ValidationError(f"Your full name must be at least 8 characters")

        if full_name.endswith('whofe'):
            raise serializers.ValidationError(f"This name cannot be registered")


        return full_name

    @staticmethod
    def get_profile_image(data):
        """ get_profile_image

        return the user's profile image
        """
        return data.get_profile_image()

    @staticmethod
    def get_date_joined(data):
        """ get_date_joined

        return the user's date joined
        """
        return data.date_joined.strftime("%m/%d/%Y")

    @staticmethod
    def get_token(data):
        """ get_token

        return the user's token
        """
        return data.get_api_token()

    class Meta:
        model = User
        extra_kwargs = {
            'password': {'write_only': True},
            #'full_name': {'read_only': True},
            'date_joined': {'read_only': True},
            'profile_image': {'read_only': True},
            'token': {'read_only': True}}

        fields = ('id', 'first_name', 'last_name', 'email', 'token',
                  'date_joined', 'password', 'profile_image')

    def create(self, validated_data):
        """ create

        Create a new user and all around good stuff here
        """
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()

        # generate some playlist
        user.generate_default_playlists()

        return user

    def to_representation(self, instance):
        """ Modify the return data based on what we're sending in

        If we are looking for something "simple", we don't have to return
        most of the files
        """
        # get the original representation
        ret = super().to_representation(instance)

        # change the date
        ret['date_joined'] = instance.date_joined.strftime("%m/%d/%Y")
        # return the modified representation
        return ret
