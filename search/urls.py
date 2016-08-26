from django.conf.urls import url

from .views import search_view, search_jobs

urlpatterns = [
    url(r'^$', search_view, name='search_search_view'),
    url(r'^jobs/$', search_jobs, name='search_jobs')
]
