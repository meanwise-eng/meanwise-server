from django.conf.urls import url

from .api import CompanyJobList, JobDetail, JobList
from .views import applyJob, getRecommendations

urlpatterns = [
    url(r'^list/$', JobList.as_view(), name='all-companies'),
    url(r'^(?P<company_slug>[-\w]+)/$', CompanyJobList.as_view(),
        name='create-list-jobs'),
    url(r'^(?P<company_slug>[-\w]+)/(?P<job_slug>[-\w]+)/$',
        JobDetail.as_view(),
        name='job-detail'),
    url(r'^(?P<company_slug>[-\w]+)/(?P<job_slug>[-\w]+)/apply/$', applyJob,
        name='applyJob'),
    url(r'^(?P<username>[0-9a-z_.]+)/recommendations/$', getRecommendations,
        name='recommendations'),
]
