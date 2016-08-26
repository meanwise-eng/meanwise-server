from django.conf.urls import url

from .views import request_invite

urlpatterns = [
    url(r'^request/$', request_invite, name='subscribe_request_invite'),
]
