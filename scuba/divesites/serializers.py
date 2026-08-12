from datetime import date

from rest_framework import serializers
from django.core.cache import cache
from django.templatetags.static import static
from django.urls import reverse

from scuba.divesites.models import Divesite, DivesiteReview, \
    DivesiteFavorite, DivesiteCheckin, DivesiteCheckinThank
import scuba.divesites.models as divesites_models

from scuba.libs.exceptions import InvalidWeatherDataException
from scuba.maps.models import Region


class DivesiteTagOptionSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField()

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_name(data):
        return data.tag.tag

    class Meta:
        """ define models, fields, etc """
        model = divesites_models.DivesiteTagOption
        fields = (
            'id',
            'name',
        )


class DivesiteSerializer(serializers.ModelSerializer):
    """ CauseSerializer

    The serializer for a program
    Function takes in a program object and converts it to appropriate
    json objects
    """
    id = serializers.SerializerMethodField()
    tags = serializers.ListSerializer(child=DivesiteTagOptionSerializer())
    difficulty_display = serializers.SerializerMethodField(read_only=True)
    banner = serializers.SerializerMethodField(read_only=True)
    lat = serializers.SerializerMethodField(read_only=True)
    long = serializers.SerializerMethodField(read_only=True)
    coords = serializers.SerializerMethodField(read_only=True)
    location = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    stats = serializers.SerializerMethodField(read_only=True)
    checkin_count = serializers.SerializerMethodField(read_only=True)
    # weather = serializers.SerializerMethodField(read_only=True)
    # checkins = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        """ Override the initialization. We're going to remove all fields
        and keep the base fields
        """
        # get the response type
        response_type = kwargs.pop('type', '')

        super().__init__(*args, **kwargs)
        if response_type == 'simple':
            self.fields.pop("checkins", None)

    @staticmethod
    def get_coords(data):
        return {
            'long': float(data.long),
            'lat': float(data.lat),
        }

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
        retval['location'] = weather['location']
        retval['location']['id'] = data.region.pk_as_str
        retval['reviews'] = [data.get_divesite_stats(date.today())]
        return retval

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_url(data):
        return reverse('site', kwargs={'url': data.url})

    @staticmethod
    def get_checkin_count(data):
        return data.checkins.filter(checkin_date=date.today()).count()

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
            'difficulty_display', 'banner', 'stats', 'checkin_count',
            'url', 'tags', 'location', 'coords',
        )

    def create(self, validated_data):
        raise NotImplementedError


class DivesiteReviewSerializer(serializers.ModelSerializer):
    """ DivesiteReviewSerializer

    The serializer for a divesite review
    """
    def __init__(self, *args, **kwargs):
        divesite = kwargs.pop('divesite', None)
        super().__init__(*args, **kwargs)

        if divesite:
            setattr(self, 'divesite', divesite)
        else:
            self.fields.pop('divesite')

    id = serializers.SerializerMethodField(read_only=True)
    review_date = serializers.SerializerMethodField(read_only=True)
    divesite = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_user(obj):
        user = obj.user
        return {
            'id': user.pk_as_str,
            'username': user.username,
            'profile_image': user.profile_image,
        }

    @staticmethod
    def get_review_date(data):
        return int(data.review_date.strftime('%s'))

    def get_divesite(self, _):
        divesite = self.divesite

        return {
            'url': reverse('site', kwargs={'url': divesite.url}),
            'name': divesite.name,
        }

    class Meta:
        """ define models, fields, etc """
        model = DivesiteReview
        fields = (
            'id',
            'divesite',
            'review',
            'rating',
            'temp_c',
            'visibility',
            'review_date',
            'user',
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
        if DivesiteReview.objects.filter(user=user, review_date=today, divesite=divesite).exists():
            raise serializers.ValidationError("You already submitted a review for today")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        data = {
            'divesite': getattr(self, 'divesite'),
            'user': user,
            'rating': validated_data['rating'],
            'review': validated_data['review'],
        }

        review = DivesiteReview.objects.create(**data)

        # add the review to the user's feed
        user.add_review_to_feed(review.id)
        return review


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


class DivesiteCheckinThankSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        divesite_checkin = kwargs.pop('divesite_checkin', None)
        setattr(self, 'divesite_checkin', divesite_checkin)
        super().__init__(*args, **kwargs)

    thank = serializers.BooleanField(default=True)

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        return DivesiteCheckinThank.objects.update_or_create(
            divesite_checkin=getattr(self, 'divesite_checkin'),
            user=self.context['request'].user,
            defaults={'is_thanked': validated_data['thank']})


class DivesiteCheckinSerializer(serializers.ModelSerializer):
    """ DivesiteCheckinSerializer

    The serializer for a divesite review
    """
    id = serializers.SerializerMethodField(read_only=True)
    checkin_date = serializers.DateField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)
    divesite_id = serializers.UUIDField()
    rating = serializers.IntegerField()

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_user(obj):
        user = obj.user
        return {
            'id': user.pk_as_str,
            'username': user.username,
            'profile_image': user.profile_image,
        }

    @staticmethod
    def get_checkin_date(data):
        return int(data.checkin_date.strftime('%s'))

    def get_divesite(self, data):
        # get the divesite from attribute
        divesite = getattr(self, 'divesite')

        return {
            'url': reverse('site', kwargs={'url': divesite.url}),
            'name': divesite.name,
        }

    def validate(self, attrs):
        user = self.context['request'].user
        today = date.today()

        if DivesiteCheckin.objects.filter(user=user,
                                          divesite=attrs['divesite_id'],
                                          checkin_date=today).count():
            raise serializers.ValidationError("You already checked in today")

        # everything is good, return
        return attrs

    @staticmethod
    def validate_temp_c(temp_c):
        if temp_c < 0 or temp_c > 100:
            raise serializers.ValidationError(f"{temp_c} is invalid")

        return temp_c

    def validate_divesite_id(self, divesite_id):
        if Divesite.objects.filter(id=divesite_id):
            return divesite_id

        raise serializers.ValidationError(f"{divesite_id} is invalid")

    @staticmethod
    def validate_visibility(visibility):
        if visibility < 0 or visibility > 1000:
            raise serializers.ValidationError(f"{visibility} is invalid")

        return visibility

    class Meta:
        """ define models, fields, etc """
        model = DivesiteCheckin
        fields = (
            'id',
            'review',
            'visibility',
            'temp_c',
            'rating',
            'checkin_date',
            'user',
            'divesite_id',
            'is_anonymous',
        )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        anonymous = validated_data.get('is_anonymous')
        checkin = DivesiteCheckin.objects.create(**validated_data)

        if not anonymous:
            checkin.user.add_checkin_to_feed(checkin.id)

        return checkin

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance.is_anonymous:
            ret['user'] = None

        divesite = Divesite.objects.get(id=ret.pop('divesite_id'))

        ret['divesite'] = {
            'url': reverse('site', kwargs={'url': divesite.url}),
            'name': divesite.name,
        }

        return ret
