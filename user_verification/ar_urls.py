from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', FindFaceView.as_view(), name='ar-find-face'),
]
