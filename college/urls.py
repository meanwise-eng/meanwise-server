from django.conf.urls import url

from .views import CollegeDetailsView, CollegeStudentsView, CollegePostsView

urlpatterns = [
    url(r'^(?P<college_id>[0-9a-f-]+)/$', CollegeDetailsView.as_view(), name='college-details'),
    url(r'^(?P<college_id>[0-9a-f-]+)/students/$', CollegeStudentsView.as_view(), name='college-students'),
    url(r'^(?P<college_id>[0-9a-f-]+)/posts/$', CollegePostsView.as_view(), name='college-posts'),
]
