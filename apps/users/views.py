from django_redis import get_redis_connection
from rest_framework import mixins
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from rest_framework.viewsets import GenericViewSet

from users import serializers
from users.models import Area, Address, User
from users.serializers import CreateUserSerializer, SubAreaSerializer, AreaSerializer, Updataser

from rest_framework_extensions.cache.mixins import ListCacheResponseMixin, RetrieveCacheResponseMixin

logger = logging.getLogger('django')


class SMSCodeView(APIView):

    def get(self, request, mobile):


        # 获取StrictRedis保存数据
        strict_redis = get_redis_connection('verify_codes')   # type: StrictRedis

        # 4. 60秒内禁止重复发送短信验证码
        send_flag = strict_redis.get('send_flag_%s' % mobile)
        if send_flag:
            return Response({'message': '发送短信过于频繁'}, status=400)
            # raise ValidationError({'message': '发送短信过于频繁'})

        # 1. 生成短信验证码
        import random
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info('sms_code: %s' % sms_code)

        # 2. 使用云通讯发送短信验证码(上线用)
        print(sms_code)

        # CCP().send_template_sms('modile', [sms_code, 5], 1)

        # 3. 保存短信验证码到Redis expiry
        strict_redis.setex('sms_%s' % mobile, 60, sms_code)     # 1分钟
        strict_redis.setex('send_flag_%s' % mobile, 60, 1)         # 1分钟过期

        return Response({'message': 'ok'})


class CreateUserView(CreateAPIView):

    serializer_class = CreateUserSerializer




class AreaView(ListCacheResponseMixin, ListAPIView):
    """查询所有的省份"""

    queryset = Area.objects.filter(parent_id=None)
    # queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer

    # 禁用分页功能
    pagination_class = None


#  /areas/440100/
class SubAreaView(RetrieveCacheResponseMixin, RetrieveAPIView):
    """查询城市或区县(查询一条区域数据)"""

    queryset = Area.objects.all()
    serializer_class = SubAreaSerializer

class AddressViewSet(mixins.CreateModelMixin, GenericViewSet):

    serializer_class = serializers.UserAddressSerializer      #序列化
    permission_classes = [IsAuthenticated]   #验证用户是否登陆

    def create(self, request, *args, **kwargs):

        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        # 获取当前登录用户的所有地址
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """ 用户地址列表数据 """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'user_id': request.user.id,
            'default_address_id': request.user.default_address_id,

            'addresses': serializer.data})  # 列表

    def destroy(self, request, pk):

        try:
            ress = Address.objects.get(pk=pk)


        except Address.DoesNotExist:
            return Response(status=404)

        ress.delete()
        # 响应请求
        return Response(status=204)


class UpdateAddrView(UpdateModelMixin,GenericAPIView):


    queryset = User.objects.all()
    serializer_class = Updataser


    def put(self, request, pk):

        return self.update(request, pk)







