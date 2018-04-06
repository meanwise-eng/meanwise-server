from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', VerifyUserView.as_view(), name='user-verification-verify'),
    url(r'^(?P<profile_id>[a-z0-9-]+)/$', UserVerificationDetailsView.as_view(),
                                          name='user-verification-details'),
]
