from django.conf.urls import url
from .views import PostAnalyticsView, PersonalAnalyticsView

urlpatterns = [
    url(r'', PostAnalyticsView.as_view()),
]
