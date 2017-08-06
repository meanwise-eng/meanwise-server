from django.conf.urls import url

from post.views import *

urlpatterns = [
    url(r'^explore/$', PostExploreView.as_view(), name='post-explore'),
    url(r'^(?P<post_id>[0-9]+)/comments/$', PostCommentList.as_view(),
        name="post-comment"),
    url(r'^(?P<post_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        PostCommentDetail.as_view(), name="comment-detail"),
    url(r'^(?P<post_id>[0-9]+)/likes/$', PostLikes.as_view(), name='post-likes'),
    url(r'^tags/autocomplete/$', AutocompleteTag.as_view()),
    url(r'^topics/autocomplete/$', AutocompleteTopic.as_view()),
]
