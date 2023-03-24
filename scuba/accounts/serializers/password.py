from rest_framework import serializers


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        """ A stub for the create method. This does nothing """
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ A stub for the create method. This does nothing """
        raise NotImplementedError
