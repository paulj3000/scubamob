from datetime import date

from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from scuba.divesites.models import Divesite, DivesiteReview, DivesiteFavorite, DivesiteDailyStats
from scuba.maps.models import Region


class DivesiteSerializer(serializers.ModelSerializer):
    """ CauseSerializer

    The serializer for a program
    Function takes in a program object and converts it to appropriate
    json objects
    """
    id = serializers.SerializerMethodField()
    difficulty_display = serializers.SerializerMethodField(read_only=True)
    banner = serializers.SerializerMethodField(read_only=True)
    lat = serializers.SerializerMethodField(read_only=True)
    long = serializers.SerializerMethodField(read_only=True)
    stats = serializers.SerializerMethodField(read_only=True)
    #weather = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_stats(data):
        weather = None
        if data.region:
            key = f'weather_{data.region.pk_as_str}'
            if cache.get(key):
                weather = cache.get(key)
            else:
                weather, _ = Region.get_weather_by_lat_long(data.lat, data.long)
                cache.set(key, weather, 3600)
                data.save()
        else:
            weather, region = Region.get_weather_by_lat_long(data.lat, data.long)
            key = f'weather_{region.pk_as_str}'
            data.region = region
            cache.set(key, weather, 3600)
            data.save()

        # attach the current conditions to the return value
        retval = data.get_divesite_stats(date.today())
        retval['condition'] = weather['current']['condition']
        return retval

    '''
    @staticmethod
    def get_weather(data):
        if data.region:
            key = f'weather_{data.region.pk_as_str}'
            if cache.get(key):
                return cache.get(key)

        weather, region = Region.get_weather_by_lat_long(data.lat, data.long)
        data.region = region
        cache.set(key, weather, 3600)
        data.save()

        return weather
    '''

    @staticmethod
    def get_banner(data):
        return data.banner

    @staticmethod
    def get_lat(data):
        return float(data.lat)

    @staticmethod
    def get_long(data):
        return float(data.long)

    @staticmethod
    def get_difficulty_display(data):
        return data.get_difficulty_display()

    class Meta:
        """ define models, fields, etc """
        model = Divesite
        fields = (
            'id', 'name', 'description', 'lat', 'long', 'difficulty',
            'difficulty_display', 'banner', 'stats',
        )

    def create(self, validated_data):
        retval = []
        file = validated_data['file']
        return Media.upload_new_media(fileinfo.name, fileinfo.content_type, fileinfo.read())


class DivesiteReviewSerializer(serializers.ModelSerializer):
    """ CauseSerializer

    The serializer for a program
    Function takes in a program object and converts it to appropriate
    json objects
    """
    def __init__(self, *args, **kwargs):
        divesite = kwargs.pop('divesite', None)
        setattr(self, 'divesite', divesite)
        super().__init__(*args, **kwargs)

    id = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    class Meta:
        """ define models, fields, etc """
        model = DivesiteReview
        fields = (
            'id',
            'review',
            'rating',
        )

    @staticmethod
    def validate_rating(rating):
        if rating < 0 or rating > 5:
            raise serializers.ValidationError(f"{rating} is invalid")

        return rating

    def validate(self, attrs):
        divesite = getattr(self, 'divesite')
        user = self.context['request'].user

        today = date.today()
        if DivesiteReview.objects.filter(user=user, review_date=today, divesite=divesite).filter():
            raise serializers.ValidationError(f"You already submitted a review for today")

        return attrs

    def create(self, validated_data):
        data = {
            'divesite': getattr(self, 'divesite'),
            'user': self.context['request'].user,
            'rating': validated_data['rating'],
            'review': validated_data['review'],
        }

        return DivesiteReview.objects.create(**data)


class DivesiteFavoriteSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        divesite = kwargs.pop('divesite', None)
        setattr(self, 'divesite', divesite)
        super().__init__(*args, **kwargs)

    favorite = serializers.BooleanField(default=True)

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}

        return DivesiteFavorite.objects.update_or_create(
            divesite=getattr(self, 'divesite'),
            user=self.context['request'].user,
            defaults={'is_favorite': validated_data['favorite']})
