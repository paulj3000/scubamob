from django.shortcuts import get_object_or_404
from django.conf.urls.static import static

from rest_framework import serializers

from scuba.accounts.models import User, UserDivesiteFavorite
from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer


class UserDivesiteFavoriteSerializer(serializers.Serializer):
    divesite_id = serializers.CharField(write_only=True)
    id = serializers.SerializerMethodField()
    divesite = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_divesite(data):
        return DivesiteSerializer(data.divesite).data

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    def validate_divesite_id(self, divesite_id):
        """ validate_divesite_id

        make sure a divesite_id coming in is valid
        """
        if not Divesite.objects.filter(id=divesite_id):
            raise serializers.ValidationError(f"{divesite_id} is not a valid divesite id")

        return divesite_id

    class Meta:
        model = UserDivesiteFavorite
        fields = ('divesite',)

    def create(self, validated_data):
        """ A stub for the create method. This does nothing """
        user = self.context['request'].user
        return user.divesites_favorites.create(divesite_id=validated_data['divesite_id'])
        from pprint import pprint
        pprint(validated_data)
        pprint(validated_data)
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ A stub for the create method. This does nothing """
        raise NotImplementedError

    def xto_representation(self, value):
        """ Modify the return data based on what we're sending in

        If we are looking for programs, we'll return that too
        """
        # get the original representation
        ret = super().to_representation(value)
        from pprint import pprint
        pprint(ret.values())

        divesites = Divesite.objects.filter(id__in=ret.values())
        pprint(divesites)

        return DivesiteSerializer(divesites, many=True).data
