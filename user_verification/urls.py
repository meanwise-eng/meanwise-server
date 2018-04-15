from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', VerifyUserView.as_view(), name='user-verification-verify'),
    url(r'^(?P<profile_uuid>[a-z0-9-]+)/$', UserVerificationDetailsView.as_view(),
                                          name='user-verification-details'),
    url(r'^(?P<profile_uuid>[a-z0-9-]+)/full-video/$', UploadAudioCheckAndVideoView.as_view(),
                                          name='user-verification-full-video'),
]
