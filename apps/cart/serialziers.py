from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from goods.models import Goods


class CartAddSerializer(serializers.Serializer):
    """添加商品到购物车的序列化器"""

    goods_id = serializers.IntegerField(label='商品id', min_value=1)
    count = serializers.IntegerField(label='数量', min_value=1)
    selected = serializers.BooleanField(label='勾选状态', default=False)

    def validate_sku_id(self, value):
        try:
            Goods.objects.get(id=value)
        except Goods.DoesNotExist:
            raise ValidationError('商品不存在')  # 400                # ok
            # raise ValidationError({'message': '商品不存在'})          # ok
            # return Response({'message': '商品不存在'}, status=400)   # error
        return value


class CartSKUSerializer(serializers.ModelSerializer):
    """
    查询购物车商品使用到的序列化器
    """
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = Goods
        fields = ('id', 'title', 'img_url', 'sell_price', 'count', 'selected')


class CartDeleteSerializer(serializers.Serializer):
    """
    删除购物车数据序列化器
    """
    sku_id = serializers.IntegerField(label='商品id', min_value=1)

    def validate_sku_id(self, value):
        try:
            sku = Goods.objects.get(id=value)
        except Goods.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value