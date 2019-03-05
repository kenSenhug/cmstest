from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from redis import StrictRedis
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.cart.serialziers import CartAddSerializer, CartDeleteSerializer, CartSKUSerializer, CartSelectAllSerializer
from goods.models import Goods


class CartView(APIView):
    # permission_classes = [IsAuthenticated]
    # POST /cart/
    # 重写父类的认证jwt的方法, 捕获异常
    def perform_authentication(self, request):
        print('-----perform_authentication-------')
        """
        drf框架在视图执行前会调用此方法进行身份认证(jwt认证)
        如果认证不通过,则会抛异常返回401状态码
        问题: 抛异常会导致视图无法执行
        解决: 捕获异常即可
        """
        try:
            super().perform_authentication(request)
        except Exception as e:
            print('perform_authentication: ', e)
    
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
        user = request.user
        # 判断是否已经登录
        # if user.is_authenticated():
            # cart_1 = {1: 2, 2: 2}
            # cart_selected_1 = {1,  2}
            # 用户已登录，获取操作Redis的StrictRedis对象


        strict_redis = get_redis_connection('cart')  # type: StrictRedis
        # 增加购物车商品数量
        strict_redis.hincrby('cart_%s' % user.id, goods_id, count)
        # 保存商品勾选状态
        if selected:
            strict_redis.sadd('cart_selected_%s' % user.id, goods_id)
        # 响应序列化数据
        return Response(s.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """查询购物车中的商品"""
        # 获取用户对象
        user = request.user
        # if user.is_authenticated():  # 判断是否已经登录
        # cart_1 = {1: 2, 2: 2}
        # cart_selected_1 = {1,  2}
        # 用户已登录，获取操作Redis的StrictRedis对象
        strict_redis = get_redis_connection('cart')  # type: StrictRedis
        # 读取购物车的商品数据，得到一个字典
        dict_data = strict_redis.hgetall('cart_%s' % user.id)  # {1: 2, 2: 2}  --> bytes
        # 读取商品勾选状态，得到一个列表
        list_data = strict_redis.smembers('cart_selected_%s' % user.id)  #  (1, )  --> bytes

        cart = {}
        # 拼接得到类似如下字典 ：
        #    {1:{'count':2, 'selected':False}, 2:{'count':2, 'selected':False}}
        for goods_id, count in dict_data.items():  # 遍历字典的键和值
            cart[int(goods_id)] = {
                'count': int(count),
                'selected': goods_id in list_data
            }

        # 查询的所有的商品对象: SKU.objects.filter(id__in=[1,2])
        goods = Goods.objects.filter(id__in=cart.keys())
        # 给商品对象新增count和selected属性
        for sku in goods:
            # 给sku对象 新增count和selected属性
            sku.count = cart.get(sku.id).get('count')
            sku.selected = cart.get(sku.id).get('selected')

        # 序列化商品对象并响应数据
        s = CartSKUSerializer(goods, many=True)
        return Response(s.data)

    def put(self, request):
        """修改购物车中的商品"""

        # 创建序列化器，校验请求参数是否合法
        s = CartAddSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        # 获取校验后的3个参数： sku_id, count, selected
        goods_id = s.validated_data.get('goods_id')
        count = s.validated_data.get('count')
        selected = s.validated_data.get('selected')

        # 获取用户对象
        user = request.user
        # user = request.user
        # 判断是否已经登录
        # if user.is_authenticated():
        # cart_1 = {1: 2, 2: 2}
        # cart_selected_1 = {1,  2}
        # 用户已登录，获取操作Redis的StrictRedis对象
        strict_redis = get_redis_connection('cart')  # type: StrictRedis
        # 修改商品数量
        strict_redis.hset('cart_%s' % user.id, goods_id, count)
        # 修改商品的勾选状态
        if selected:
            strict_redis.sadd('cart_selected_%s' % user.id, goods_id)
        else:
            strict_redis.srem('cart_selected_%s' % user.id, goods_id)
        # 响应序列化数据
        return Response(s.data)

    def delete(self, request):
        """删除购物车的中商品"""

        # 创建序列化器，校验sku_id是否合法
        s = CartDeleteSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        # 获取校验后的sku_id,
        goods_id = s.validated_data.get('sku_id')

        # 获取用户对象
        # user = request.user
        user = request.user
        user.id = user.id
        # 通过cookie保存购物车数据（base64字符串）
        response = Response(status=204)

        # 判断是否已经登录
        # if user.is_authenticated():
        # cart_1 = {1: 2, 2: 2}
        # cart_selected_1 = {1, 2}
        # 用户已登录，获取操作Redis的StrictRedis对象
        strict_redis = get_redis_connection('cart')  # type: StrictRedis
        # 删除商品  hdel cart_1 1
        strict_redis.hdel('cart_%s' % user.id, goods_id)
        # 删除商品勾选状态 srem cart_selected_1 1
        strict_redis.srem('cart_selected_%s' % user.id, goods_id)
        # 响应数据
        return response


class CartSelectAllView(APIView):
    """
    购物车全选和全不选
    """

    def perform_authentication(self, request):
        """
        drf框架在视图执行前会调用此方法进行身份认证(jwt认证)
        如果认证不通过,则会抛异常返回401状态码
        问题: 抛异常会导致视图无法执行
        解决: 捕获异常即可
        """
        try:
            super().perform_authentication(request)
        except Exception:
            pass

    def put(self, request):
        """全选或全不选"""
        serializer = CartSelectAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data['selected']

        user = request.user
        
        # 用户已登录，在redis中保存
        #  cart_1 = {1: 2, 2: 2}
        # cart_selected_1 = {1}
        redis_conn = get_redis_connection('cart')
        # hkeys cart_1    (1, 2)    获取hash所有的字段名 
        sku_id_list = redis_conn.hkeys('cart_%s' % user.id)  # （1, 2） bytes

        if selected:  # 全选

            redis_conn.sadd('cart_selected_%s' % user.id, *sku_id_list)
        else:  # 取消全选
            redis_conn.srem('cart_selected_%s' % user.id, *sku_id_list)
        return Response({'message': 'OK'})


