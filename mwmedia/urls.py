from django.conf.urls import url

from mwmedia.views import *

urlpatterns = [
    url(r'^upload/(?P<filename>.+)$', MediaUploadView.as_view(), name='media-upload'),
]
