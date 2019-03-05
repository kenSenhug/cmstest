from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from apps.users import views

urlpatterns = [

    url(r'^sms_code/(\d+)/$',views.SMSCodeView.as_view()),  #获取短信验证码
    url(r'^users/$',views.CreateUserView.as_view()),        #注册
    url(r'^authorizations/$',obtain_jwt_token),             #登陆
    url(r'^areas/$',views.AreaView.as_view()),              #获取省数据
    url(r'^areas/(?P<pk>\d+)/$',views.SubAreaView.as_view()),      #获取市，县数据


]
router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')
urlpatterns += router.urls
