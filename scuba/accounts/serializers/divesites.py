from django.shortcuts import get_object_or_404
from django.conf.urls.static import static

from rest_framework import serializers

from scuba.accounts.models import User, UserDivesiteFavorite
from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer


class UserDivesiteFavoriteSerializer(serializers.ModelSerializer):
    divesite_id = serializers.SerializerMethodField()

    @staticmethod
    def get_divesite_id(data):
        return data.divesite.pk_as_str

    class Meta:
        model = UserDivesiteFavorite
        fields = ('divesite_id',)

    def create(self, validated_data):
        """ A stub for the create method. This does nothing """
        raise NotImplementedError

    def update(self, instance, validated_data):
        """ A stub for the create method. This does nothing """
        raise NotImplementedError

    def to_representation(self, value):
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
