from rest_framework import serializers

from scuba.accounts.models import UserCollection, UserCollectionItem
from scuba.divesites.models import Divesite


class CollectionSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(required=False)
    divesite_id = serializers.UUIDField(write_only=True, required=False)
    name = serializers.CharField()
    is_public = serializers.BooleanField()
    is_active = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        """ Override the initialization. We're going to remove all fields
        and keep the base fields
        """
        # get the response type
        divesite = kwargs.pop('divesite', None)

        super().__init__(*args, **kwargs)
        if divesite:
            setattr(self, 'divesite', divesite)
        else:
            self.fields.pop('is_active', None)

    def validate_divesite_id(self, data):
        divesite = Divesite.objects.filter(id=data)

        if not divesite:
            raise serializers.ValidationError(f"'{data}' is not a valid divesite id")

        setattr(self, 'divesite', divesite)
        return data

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    def get_is_active(self, data):
        instance = getattr(self, 'divesite')
        item = UserCollectionItem.objects.filter(collection=data.id, instance_id=instance.id)
        return True if item.count() else False

    class Meta:
        model = UserCollection
        fields = ('id', 'name', 'is_public', 'is_active', 'divesite_id',)

    def create(self, validated_data):
        user = self.context['request'].user
        is_public = validated_data['is_public']
        name = validated_data['name']
        divesite_id = validated_data.get('divesite_id')

        collection = user.collections.create(name=name, is_public=is_public)
        if divesite_id:
            collection.items.create(instance_id=divesite_id, instance_type=0)

        return collection


class CollectionItemSerializer(serializers.ModelSerializer):
    instance_id = serializers.UUIDField()
    instance_type = serializers.IntegerField()
    is_active = serializers.BooleanField()

    @staticmethod
    def validate_instance_type(instance_type):
        types = [x[0] for x in UserCollectionItem.COLLECTION_VALUES]

        if instance_type not in types:
            raise serializers.ValidationError(f"'{instance_type}' is not cool")

        return instance_type

    class Meta:
        model = UserCollectionItem
        fields = ('id', 'instance_type', 'instance_id', 'is_active',)

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        instance_type = validated_data['instance_type']
        instance_id = validated_data['instance_id']
        collection = validated_data['collection']
        is_active = validated_data['is_active']

        UserCollectionItem.objects.filter(collection=collection, instance_id=instance_id).delete()

        if is_active:
            collection.add_to_collection(instance_type, instance_id)

        return {
            'collection': collection,
            'is_active': is_active,
        }
