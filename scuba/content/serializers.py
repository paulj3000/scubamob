from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator
from rest_framework import serializers

from scuba.content.models import NewsArticle


class NewsArticleSerializer(serializers.ModelSerializer):
    """ NewsArticleSerializer

    A lightweight representation of a published news article, used by the
    homepage dashboard's news widget.
    """
    id = serializers.SerializerMethodField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    excerpt = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_id(data):
        return data.pk_as_str

    @staticmethod
    def get_url(data):
        return reverse('news_article', kwargs={'url': data.url})

    @staticmethod
    def get_excerpt(data):
        return Truncator(strip_tags(data.content)).words(30)

    class Meta:
        """ define models, fields, etc """
        model = NewsArticle
        fields = ('id', 'title', 'url', 'excerpt', 'published_date')
