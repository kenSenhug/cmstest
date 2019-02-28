
from django.conf.urls import url

from news import views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^topnews/$', views.TopNewView.as_view()),
    url(r'^categorynews/$', views.CategoryNewsView.as_view()),
]
