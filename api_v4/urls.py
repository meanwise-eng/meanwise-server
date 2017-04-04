from django.conf.urls import include, url

from rest_framework import routers
router = routers.SimpleRouter()

from userprofile.views import *
from post.views import *
from mnotifications.views import *

#router.register(r'user/userprofile', UserProfileViewSet)
router.register(r'post', PostViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'share', ShareViewSet)

router.register(r'search/post', PostSearchView, base_name="post-search")
router.register(r"search/userprofile", UserProfileSearchView, base_name="userprofile-search")

urlpatterns = [
    url(r'custom_auth/', include('custom_auth.urls')),
    url(r'^', include(router.urls)),
    url(r'^user/userprofile/$', UserProfileList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/userprofile/$', UserProfileDetail.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/change/password/$', ChangePasswordView.as_view()),
    url(r'^user/forgot/password/$', ForgotPasswordView.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/friends/$', FriendsList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/friends/remove/$', RemoveFriend.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/posts/$', UserPostList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[0-9]+)/$', UserPostDetail.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/friends/posts/$', UserFriendsPostList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/interests/posts/$', UserInterestsPostList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/home/feed/$', UserHomeFeed.as_view()),
    url(r'^posts/(?P<post_id>[0-9]+)/comments/$', PostCommentList.as_view()),
    url(r'^posts/(?P<post_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$', PostCommentDetail.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[0-9]+)/like/$', UserPostLike.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[0-9]+)/unlike/$', UserPostUnLike.as_view()),
    url(r'^posts/tags/autocomplete/$', AutocompleteTag.as_view()),
    url(r'^posts/topics/autocomplete/$', AutocompleteTopic.as_view()),
    url(r'^interests/(?P<interest_id>[0-9]+)/topics/trending/$', TrendingTopicForInterest.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/notifications/new/$', UserNotificationsNew.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/notifications/latest/$', UserNotificationsLatest.as_view()),
    url(r'^profession/$', ProfessionListView.as_view()),
    url(r'^skill/$', SkillListView.as_view()),
    url(r'^interest/$', InterestListView.as_view()),
    
]
