from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^(?P<college_id>[0-9a-f-]+)/$', CollegeDetailsView.as_view(), name='college-details'),
    url(r'^(?P<college_id>[0-9a-f-]+)/students/$', CollegeStudentsView.as_view(), name='college-students'),
    url(r'^(?P<college_id>[0-9a-f-]+)/posts/$', CollegePostsView.as_view(), name='college-posts'),
    url(r'^(?P<college_id>[0-9a-f-]+)/follow/$', FollowCollegeView.as_view(), name='college-follow'),
    url(r'^(?P<college_id>[0-9a-f-]+)/unfollow/$', UnfollowCollegeView.as_view(), name='college-unfollow'),
]
