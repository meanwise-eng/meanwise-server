from django.conf.urls import url

from post.views import *

urlpatterns = [
    url(r'^explore/$', PostExploreView.as_view(), name='post-explore'),
    url(r'^trending/$', PostExploreTrendingView.as_view(), name='post-trending'),
    url(r'^(?P<post_id>[0-9]+)/comments/$', PostCommentList.as_view(),
        name="post-comment"),
    url(r'^(?P<post_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$',
        PostCommentDetail.as_view(), name="comment-detail"),
    url(r'^(?P<post_id>[0-9]+)/likes/$', PostLikes.as_view(), name='post-likes'),
    url(r'^(?P<post_id>[0-9]+)/related/$', PostRelatedView.as_view(), name='post-related'),
    url(r'^(?P<post_id>[0-9]+)/$', PostDetails.as_view(), name='post-details'),
    url(r'^tags/autocomplete/$', AutocompleteTag.as_view()),
    url(r'^topics/autocomplete/$', AutocompleteTopic.as_view()),
]
