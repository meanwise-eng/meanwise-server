from django.conf.urls import include, url

from subscribe import urls as subscribe_urls
from account_profile import urls as account_profile_urls
from interests import urls as interests_urls
from geography import urls as geography_urls
from search import urls as search_urls
from recommendation import urls as recommendation_urls
from jobs import urls as jobs_urls
from notifications import urls as notifications_urls
from works import urls as work_urls

from .views import private_view

urlpatterns = [
    url(r'subscribe/', include(subscribe_urls)),
    url(r'interests/', include(interests_urls)),
    url(r'geo/', include(geography_urls)),
    url(r'search/', include(search_urls)),
    url(r'', include(recommendation_urls)),
    url(r'', include(jobs_urls)),
    url(r'', include(notifications_urls)),
    url(r'', include(work_urls)),
    url(r'', include(account_profile_urls)),
    url(r'^', include('company.urls')),
    url(r'^jobs/', include('jobs.urls')),
    url(r'^pages/', include('pages.urls')),
    url(r'^stripe/', include('djstripe.urls')),
    url(r'^candidate_manager/', include('candidate_manager.urls')),
    url(r'rest_auth/', include('rest_auth.urls'))
]
