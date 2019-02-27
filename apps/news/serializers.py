
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from news.models import News, NewsCategory


class TopNewSerializer(ModelSerializer):

    class Meta:
        model = News
        fields = ("id", "title", "create_time", "click", 'img_url', 'zhaiyao')


class SonCategoryNewsSerializer(ModelSerializer):

    class Meta:
        model = NewsCategory
        fields = ("id", "title")


class CategoryNewsSerializer(ModelSerializer):
    newscategory_set = SonCategoryNewsSerializer(many=True, read_only=True)

    class Meta:
        model = NewsCategory
        fields = ("id", "title", "newscategory_set")

