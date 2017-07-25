from django.conf.urls import url
from .views import PostAnalyticsView

urlpatterns = [
    url(r'seen-posts/$', PostAnalyticsView.as_view())
]