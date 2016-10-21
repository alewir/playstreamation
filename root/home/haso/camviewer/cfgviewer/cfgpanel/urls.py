from django.conf.urls import url

from . import views

app_name = "config"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^service/$', views.service_input, name='service'),
]
