from django.conf.urls import url

from .api import NotificationAPIView
from .views import mark_read

urlpatterns = [
    url(r'^notifications/$', NotificationAPIView.as_view(),
        name='stream_notifications'),
    url(r'^notifications/read/$', mark_read,
        name='stream_notifications_makr_read'),
]
