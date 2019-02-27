from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from rest_framework.views import APIView

from news import serializers
from news.models import News, NewsCategory


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


class CategoryNewsView(APIView):

    def get(self, request):
        category_query = NewsCategory.objects.filter(parent_id=0)
        data_list = []
        for cate in category_query:
            category_query_dict = serializers.CategoryNewsSerializer(cate).data

            son_cate = cate.newscategory_set.all()
            ids_list = []
            for cate in son_cate:
                ids_list.append(cate.id)
            category_query_dict['news'] = News.objects.filter(category_id__in=ids_list).exclude(img_url='').order_by('-create_time')[0:4]
            category_query_dict['news'] = serializers.TopNewSerializer(category_query_dict['news'], many=True).data
            category_query_dict['top'] = News.objects.filter(category_id__in=ids_list).order_by('-click')[0:8]
            category_query_dict['top'] = serializers.TopNewSerializer(category_query_dict['top'], many=True).data

            data_list.append(category_query_dict)
            print(data_list)

        data = {
            'data_list': data_list,
        }
        return Response(data)