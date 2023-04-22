from datetime import date

from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.templatetags.static import static

from scuba.divesites.models import Divesite, DivesiteReview, \
    DivesiteFavorite, DivesiteDailyStats, DivesiteCheckin

from scuba.libs.exceptions import InvalidWeatherDataException
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
    # weather = serializers.SerializerMethodField(read_only=True)

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
                try:
                    weather, _ = Region.get_weather_by_lat_long(data.lat, data.long)
                    cache.set(key, weather, 3600)
                    data.save()
                except InvalidWeatherDataException:
                    data.query_weather = False
                    data.save()
                    return {}
        else:
            try:
                weather, region = Region.get_weather_by_lat_long(data.lat, data.long)
                key = f'weather_{region.pk_as_str}'
                data.region = region
                cache.set(key, weather, 3600)
                data.save()
            except InvalidWeatherDataException:
                data.query_weather = False
                data.save()
                return {}

        # attach the current conditions to the return value
        retval = {}
        # retval['condition'] = weather['current'].pop('condition')
        retval['weather'] = weather['current']
        retval['reviews'] = [data.get_divesite_stats(date.today())]
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
        return static(data.banner)

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
    """ DivesiteReviewSerializer

    The serializer for a divesite review
    """
    def __init__(self, *args, **kwargs):
        divesite = kwargs.pop('divesite', None)
        setattr(self, 'divesite', divesite)
        super().__init__(*args, **kwargs)

    id = serializers.SerializerMethodField(read_only=True)
    review_date = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_review_date(data):
        return int(data.review_date.strftime('%s'))

    class Meta:
        """ define models, fields, etc """
        model = DivesiteReview
        fields = (
            'id',
            'review',
            'rating',
            'temp_c',
            'visibility',
            'review_date',
        )

    @staticmethod
    def validate_rating(rating):
        if rating < 0 or rating > 5:
            raise serializers.ValidationError(f"{rating} is invalid")

        return rating

    @staticmethod
    def validate_temp_c(temp_c):
        if temp_c < 0 or temp_c > 100:
            raise serializers.ValidationError(f"{temp_c} is invalid")

        return temp_c

    @staticmethod
    def validate_visibility(visibility):
        if visibility < 0 or visibility > 1000:
            raise serializers.ValidationError(f"{visibility} is invalid")

        return visibility

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


class DivesiteCheckinSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    checkin_date = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_checkin_date(data):
        return int(data.checkin_date.strftime('%s'))

    def validate(self, attrs):
        divesite = getattr(self, 'divesite')
        user = self.context['request'].user
        today = date.today()

        if DivesiteCheckin.objects.filter(user=user, divesite=divesite, checkin_date=today).count():
            raise serializers.ValidationError("You already checked in today")

        # everything is good, return
        return attrs

    @staticmethod
    def validate_temp_c(temp_c):
        if temp_c < 0 or temp_c > 100:
            raise serializers.ValidationError(f"{temp_c} is invalid")

        return temp_c

    @staticmethod
    def validate_visibility(visibility):
        if visibility < 0 or visibility > 1000:
            raise serializers.ValidationError(f"{visibility} is invalid")

        return visibility

    def __init__(self, *args, **kwargs):
        divesite = kwargs.pop('divesite', None)
        setattr(self, 'divesite', divesite)
        super().__init__(*args, **kwargs)

    class Meta:
        """ define models, fields, etc """
        model = DivesiteCheckin
        fields = (
            'id',
            'note',
            'visibility',
            'temp_c',
            'checkin_date',
        )

    def create(self, validated_data):
        data = {
            'divesite': getattr(self, 'divesite'),
            'user': self.context['request'].user,
            'note': validated_data['note'],
        }

        return DivesiteCheckin.objects.create(**data)
