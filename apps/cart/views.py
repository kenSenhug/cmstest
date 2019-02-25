from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.cart.serialziers import CartAddSerializer


class CartView(APIView):
    # permission_classes = [IsAuthenticated]
    # POST /cart/
    def post(self, request):
        """添加商品到购物车"""
        # user=request.data.get("user", 1)
        # 创建序列化器，校验请求参数是否合法
        s = CartAddSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        # s.save()

        # 方式1:
        # 获取校验后的3个参数： sku_id, count, selected
        goods_id = s.validated_data.get('goods_id')
        count = s.validated_data.get('count')
        selected = s.validated_data.get('selected')

        # 方式2:
        # sku_id = request.data.get('sku_id')
        # count = request.data.get('count')
        # selected = request.data.get('selected')

        # 获取用户对象
        # user = request.user

        # 判断是否已经登录
        # if user.is_authenticated():
            # cart_1 = {1: 2, 2: 2}
            # cart_selected_1 = {1,  2}
            # 用户已登录，获取操作Redis的StrictRedis对象

        user_id = 1
        strict_redis = get_redis_connection('cart')  # type: StrictRedis
        # 增加购物车商品数量
        strict_redis.hincrby('cart_%s' % user_id, goods_id, count)
        # 保存商品勾选状态
        if selected:
            strict_redis.sadd('cart_selected_%s' % user_id, goods_id)
        # 响应序列化数据
        return Response(s.data, status=status.HTTP_201_CREATED)


