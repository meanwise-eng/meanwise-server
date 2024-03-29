from django.conf.urls import url
from rest_framework.authtoken import views

from custom_auth.views import *

urlpatterns = [
    url(r'^user/register/$', RegisterUserView.as_view(), name='register_user'),
    url(r'^api-token-auth/', views.obtain_auth_token, name="api-token"),
    url(r'^user/verify-username', verify_username, name="verify-username"),
    url(r'^user/verify-email', verify_user, name='verify-email'),
    url(r'^user/verify', verify_user),
    url(r'^fetch/token/', FetchToken.as_view(), name='fetch-token'),
]
