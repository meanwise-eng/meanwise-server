from django.conf.urls import url

from .api import InterestListAPIView
from .views import follow_unfollow_interest

urlpatterns = [
    url('^$', InterestListAPIView.as_view()),
    url('^(?P<interest_id>[0-9]+)/(?P<action>(follow|unfollow))/$',
        follow_unfollow_interest, name='interests_follow_interest')
]
