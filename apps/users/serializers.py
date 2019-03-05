import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer


from users.models import User, Area, Address


class CreateUserSerializer(ModelSerializer):
    """注册用户接口使用的序列化器
    """
    # 新增三个数据库表中没有的,但需要校验的参数: 确认密码,短信验证码, 同意用户协议
    password2 = serializers.CharField(label='确认密码', min_length=8, max_length=20, write_only=True)
    sms_code = serializers.CharField(label='短信验证码', max_length=6, write_only=True)
    allow = serializers.BooleanField(label='同意用户协议', default=False, write_only=True)

    # 新增一个用于序列化的字段, 需要返回给调用的客户端
    token = serializers.CharField(label='jwt字符串', read_only=True)

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if not value:
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        # 判断两次密码
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        mobile = attrs.get('mobile')
        # 判断短信验证码
        strict_redis = get_redis_connection('verify_codes')  # type: StrictRedis
        # 获取redis中保存的正确的短信验证码
        real_sms_code = strict_redis.get('sms_%s' % mobile)   # bytes -> str

        print(real_sms_code.decode())
        if real_sms_code is None:
            raise ValidationError('验证码无效')

        # 获取用户传递的短信验证码
        sms_code = attrs.get('sms_code')
        # 比较短信验证码是否相等, 不相等提示出错信息
        if real_sms_code.decode() != sms_code:
            raise ValidationError('验证码不正确')

        return attrs

    def create(self, validated_data):
        # 自定义保存一条用户数据, 指定要保存哪些字段

        # user = User.objects.create(                   # 密码不会加密
        user = User.objects.create_user(                # 会对密码加密
            username=validated_data.get('username'),
            password=validated_data.get('password'),
            mobile=validated_data.get('mobile')
        )

        # todo: 生成jwt字符串
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 生payload部分的方法(函数)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt的方法(函数)
        #  {'exp': xxx, 'email': '', 'user_id': 1, 'username': 'admin'}
        # user：登录的用户对象
        payload = jwt_payload_handler(user)  # 生成payload, 得到字典
        token = jwt_encode_handler(payload)  # 生成jwt字符串

        # 给user对象新增一个token的属性
        user.token = token

        return user




    class Meta:
        model = User   # 关联的模型类
        fields = ('id', 'username', 'password', 'mobile',
                  'password2', 'sms_code', 'allow', 'token')

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }


class AreaSerializer(ModelSerializer):
    """查询所有省份用到的序列化器"""

    class Meta:
        model = Area
        fields = ('id', 'name')


class SubAreaSerializer(ModelSerializer):
    """查询一条区域数据时用到的序列化器"""

    # 模型类related_name的值, 不能改
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器: 序列化 + 校验参数
    """
    # 序列化时返回省市区的名称
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    # 新增地址时需要传递省市区id
    province_id = serializers.IntegerField(label='省ID')
    city_id = serializers.IntegerField(label='市ID')
    district_id = serializers.IntegerField(label='区ID')

    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """ 保存 """
        # 补充一个字段： 收件地址所属用户, 再保存到数据库表中
        validated_data['user'] = self.context['request'].user # 获取当前登录用户对象
        return super().create(validated_data)




    class Meta:
        model = Address
        # 新增地址，不需要用户传递user到服务器，服务器可以自动获取到当前登录用户对象
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')



class Updataser(ModelSerializer):

    def update(self, instance, validated_data):
        instance.default_address=validated_data.get('default_address')
        instance.save()
        return instance


    class Meta:
        model=User
        filter=('default_address')