from django.conf.urls import url

from post.views import *

urlpatterns = [
	url(r'^(?P<post_id>[0-9]+)/likes/$', PostLikes.as_view(), name='post-likes'),

]