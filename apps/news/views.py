from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from rest_framework.views import APIView

from news import serializers
from news.models import News


class TopNewView(APIView):
    def get(self, request):
        carousel_news = News.objects.filter(is_slide=True).exclude(img_url='')
        recommended_news = News.objects.order_by('-create_time')[0:10]
        picture_news = News.objects.exclude(img_url='').order_by('-click')[0:4]
        # print(picture_news)
        carousel_news = serializers.TopNewSerializer(carousel_news, many=True).data
        recommended_news = serializers.TopNewSerializer(recommended_news, many=True).data
        picture_news = serializers.TopNewSerializer(picture_news, many=True).data

        data = {
            'carousel_news': carousel_news,
            'recommended_news': recommended_news,
            'picture_news': picture_news,
        }
        return Response(data)
