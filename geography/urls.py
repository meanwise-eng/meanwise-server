from django.conf.urls import url

from .api import LocationListAPIView, CityListAPIView

urlpatterns = [
    url(r'^locations/$', LocationListAPIView.as_view()),
    url(r'^cities/$', CityListAPIView.as_view()),
]
