from django.conf.urls import url

from .views import *

urlpatterns = [
	url(r'^(?P<platform>(iOS|Android))/(?P<version>[0-9.]+)/$', VersionView.as_view()),

]