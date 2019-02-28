from rest_framework import serializers

from goods.models import Goods, GoodsCategory, GoodsAlbum


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ('id', 'title', 'img_url')


class GoodsCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ('id', 'title', 'parent')


class GoodsIndexCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ('id', 'title', 'img_url', 'stock', 'market_price', 'sell_price', 'create_time',)


class GoodsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = '__all__'


class GoodspictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsAlbum
        fields = '__all__'