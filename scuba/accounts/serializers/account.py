from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from rest_framework import serializers

from scuba.accounts.models import User


class RegisterSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField(read_only=True)
    profile_image = serializers.CharField(read_only=True)

    @staticmethod
    def get_id(data):
        """ get_id

        return the user's id (as uuid) without the dashes
        """
        return data.pk_as_str

    @staticmethod
    def get_token(data):
        return data.get_api_token()

    def validate_email(self, email):
        """ validate_plan

        Validate the plan id coming in
        """
        if User.objects.filter(email=email).count():
            raise serializers.ValidationError(f"Email address {email} is already registered")

        return email

    def validate_username(self, username):
        """ validate_username

        Validate the username coming in
        """
        if len(username) < 5 or len(username) > 40:
            raise serializers.ValidationError(f"Username {username} is an invalid length")

        if User.objects.filter(username=username).count():
            raise serializers.ValidationError(f"Username {username} is already registered")

        return username

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'])

        user.set_password(validated_data['password'])
        return user


class LoginSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.DateTimeField(required=False, read_only=True)
    profile_image = serializers.SerializerMethodField(read_only=True)
    token = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
    )

    confirmed = serializers.SerializerMethodField(read_only=True)
    email = serializers.CharField(label=_("Email"), required=False)
    username = serializers.CharField(label=_("Username"), required=False)
    device = serializers.CharField(default='mobile', write_only=True)
    ip_address = serializers.CharField(default='0.0.0.0', write_only=True)

    def validate(self, attrs):
        """ validate

        validate the data coming in. Make sure the user can authenticate, then
        return it.
        Raises: validation exception if the user has cannot authenticate
        """
        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')
        device = attrs.get('device')
        ip_address = attrs.get('ip_address')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')

        elif username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            print(f"USERNAME {username}")
            print(f"USERNAME {username}")
            print(f"USERNAME {username}")
            print(f"USERNAME {username}")

            print(user)
            print(user)
            print(user)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email or username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        # now add the user's login info
        user.add_login(ip_address, 'US', device)

        return user

    @staticmethod
    def get_profile_image(data):
        """ get_profile_image

        return the user's profile image
        """
        return data.get_profile_image()

    @staticmethod
    def get_confirmed(data):
        return data.confirmed

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

    @staticmethod
    def get_id(data):
        """ get_id

        return the user's id (as uuid) without the dashes
        """
        return data.pk_as_str

    class Meta:
        model = User
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True},
            'profile_image': {'read_only': True},
            'email': {'read_only': True},
            'username': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'device': {'write_only': True},
            'ip_address': {'write_only': True},
            'token': {'read_only': True}}

        fields = ('id', 'first_name', 'last_name', 'email', 'token', 'device',
                  'confirmed', 'username',
                  'date_joined', 'password', 'profile_image', 'ip_address',)

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
