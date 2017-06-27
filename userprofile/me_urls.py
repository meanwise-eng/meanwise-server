from django.conf.urls import url

from userprofile.views import *

urlpatterns = [
	url(r'^invite-code/$', SetInviteCodeView.as_view()),
	url(r'^$', LoggedInUserProfile.as_view())
]