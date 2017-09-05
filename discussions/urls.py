from django.conf.urls import url

from discussions.views import *

urlpatterns = [
    url(r'^$', DiscussionListView.as_view(), name='discussions-list'),
]
