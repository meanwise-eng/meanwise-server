from django.conf.urls import url
from .views import PostAnalyticsView, PersonalAnalyticsView

urlpatterns = [
    url(r'^$', PostAnalyticsView.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/$', PersonalAnalyticsView.as_view()),
]
