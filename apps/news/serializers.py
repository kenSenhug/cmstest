
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from news.models import News


class TopNewSerializer(ModelSerializer):

    class Meta:
        model = News
        fields = ("id", "title", "create_time", "click", 'img_url')
