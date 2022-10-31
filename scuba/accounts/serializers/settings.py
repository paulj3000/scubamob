from pprint import pprint

from rest_framework import serializers
from scuba.accounts.models import User, UserEmail, UserSetting


class UserEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    #is_primary = serializers.BooleanField()

    @staticmethod
    def validate_email(email):
        """ validate_email

        make sure the email coming in hasn't been used yet
        """
        if UserEmail.objects.filter(email=email):
            raise serializers.ValidationError(f"This email has already been used")

        return email

    class Meta:
        model = UserEmail

        extra_kwargs = {
            'id': {'read_only': True}
        }

        fields = ('id', 'email', 'is_primary',)

    def create(self, validated_data):
        """ create

        Create a new user and all around good stuff here
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PrimaryEmailSerializer(serializers.ModelSerializer):
    is_primary = serializers.BooleanField()

    @staticmethod
    def validate_is_primary(is_primary):
        """ validate_email

        make sure the email coming in hasn't been used yet
        """
        if is_primary:
            raise serializers.ValidationError(f"This email is already the primary email")

        return is_primary

    class Meta:
        model = UserEmail
        extra_kwargs = {
            'email': {'read_only': True}
        }
        fields = ('is_primary',)

    def update(self, instance, validated_data):
        """ create

        Create a new user and all around good stuff here
        """
        return self.context['request'].user.set_primary_email(instance.id)


class UserSettingSerializer(serializers.ModelSerializer):
    @staticmethod
    def xvalidate_is_primary(is_primary):
        """ validate_email

        make sure the email coming in hasn't been used yet
        """
        if is_primary:
            raise serializers.ValidationError(f"This email is already the primary email")

        return is_primary

    class Meta:
        model = UserSetting
        fields = ('value', 'setting',)
        extra_kwargs = {
            'setting': {'read_only': True}
        }

    def update(self, instance, validated_data):
        """ create

        Create a new user and all around good stuff here
        """
        return self.context['request'].user.set_primary_email(instance.id)

    def to_representation(self, instance):
        """ Modify the return data based on what we're sending in

        If we are looking for something "simple", we don't have to return
        most of the files
        """
        # get the original representation
        ret = super().to_representation(instance)

        from collections import OrderedDict

        from pprint import pprint
        pprint(ret)


        # change the date
        #ret['date_joined'] = instance.date_joined.strftime("%m/%d/%Y")
        # return the modified representation
        return ret
