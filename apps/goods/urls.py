from django.conf.urls import url

from goods import views

urlpatterns = [
    url(r'^index/$', views.GoodsCommendView.as_view()),
    url(r'^goods_category/$', views.CategoriesGoodsView.as_view()),
    url(r'^list/category=(?P<pk>\d+)[&,?]ordering=(?P<order>.*)/$', views.CategoryView.as_view()),
    url(r'^detail/goods=(?P<pk>\d+)/$', views.GoodsDetailView.as_view()),
]
