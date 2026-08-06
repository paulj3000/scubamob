import datetime
from dateutil.relativedelta import relativedelta

from rest_framework import serializers

from scuba.accounts.models import User


class SetUsernameSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, username):
        """ validate_username

        Make sure the username isn't already taken by a different user.
        """
        taken = User.objects.filter(username=username)
        if self.instance is not None:
            taken = taken.exclude(pk=self.instance.pk)

        if taken.exists():
            raise serializers.ValidationError(f"Username {username} is already registered")

        return username

    def update(self, instance, validated_data):
        """ set the caller's username to the validated value """
        instance.username = validated_data['username']
        instance.save()
        return instance


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()

    @staticmethod
    def validate_password(password):
        """ validate password """

        if len(password) < 8:
            raise serializers.ValidationError("Password needs to be longer")

        return password

    def update(self, instance, validated_data):
        """ set the caller's password to the validated value """
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def create(self, validated_data):
        raise NotImplementedError


class CreateUserSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
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
    def validate_username(username):
        '''
        validate_username
        make sure the username is unique
        '''
        if User.objects.filter(username=username).count():
            raise serializers.ValidationError(f"'{username}' has already registered")
        return username

    @staticmethod
    def validate_password(password):
        # for now, validate the password is at least eight chars
        if len(password) < 8:
            raise serializers.ValidationError("Password must be eight characters")

        return password

    @staticmethod
    def validate_date_of_birth(date_of_birth):
        '''
        validate_date_of_birth
        make sure the user is at least 13 years old.
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
        username = validated_data['username']

        kwargs = {
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'username': username,
        }

        return User.objects.create_user(email, password, **kwargs)
