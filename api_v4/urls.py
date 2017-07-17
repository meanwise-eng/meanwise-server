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
router.register(r'autocomplete/profession', ProfessionSearchView, base_name="profession-search")
router.register(r'autocomplete/skill', SkillSearchView, base_name="skill-search")

urlpatterns = [
    url(r'custom_auth/', include('custom_auth.urls')),
    url(r'^', include(router.urls)),
    url(r'^user/userprofile/$', UserProfileList.as_view(), name="profile-list"),
    url(r'^user/(?P<user_id>[0-9]+)/userprofile/$', UserProfileDetail.as_view(), name="profile-detail"),
    url(r'^user/(?P<user_id>[0-9]+)/change/password/$', ChangePasswordView.as_view(), name="change-password"),
    url(r'^user/forgot/password/$', ForgotPasswordView.as_view(), name="forget-password"),
    url(r'^user/(?P<user_id>[0-9]+)/friends/$', FriendsList.as_view(), name="friend"),
     url(r'^user/(?P<user_id>[0-9]+)/friends/$', FriendsList.as_view(), name='friends-list'),
    url(r'^user/(?P<user_id>[0-9]+)/friends/remove/$', RemoveFriend.as_view(), name="remove-friend"),
    url(r'^user/(?P<user_id>[0-9]+)/posts/$', UserPostList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[0-9]+)/$', UserPostDetail.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/friends/posts/$', UserFriendsPostList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/interests/posts/$', UserInterestsPostList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/home/feed/$', UserHomeFeed.as_view()),
    url(r'^posts/(?P<post_id>[0-9]+)/comments/$', PostCommentList.as_view()),
    url(r'^posts/(?P<post_id>[0-9]+)/comments/(?P<comment_id>[0-9]+)/$', PostCommentDetail.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[0-9]+)/like/$', UserPostLike.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[0-9]+)/unlike/$', UserPostUnLike.as_view()),
    url(r'^story/(?P<story_id>[0-9]+)/', StoryDetail.as_view(), name='post-story'),
    url(r'^posts/tags/autocomplete/$', AutocompleteTag.as_view()),
    url(r'^posts/topics/autocomplete/$', AutocompleteTopic.as_view()),
    url(r'^posts/', include('post.urls')),
    url(r'^interests/(?P<interest_id>[0-9]+)/topics/trending/$', TrendingTopicForInterest.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/notifications/new/$', UserNotificationsNew.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/notifications/latest/$', UserNotificationsLatest.as_view()),
    url(r'^amazon/notification/device/register/$', AmazonNotificationAddDevice.as_view()),
    url(r'^amazon/notification/device/delete/$', AmazonNotificationDeleteDevice.as_view()),
    url(r'^amazon/notification/message/send/$', AmazonNotificationSendMessage.as_view()),
    url(r'^invite/code/valid/$', ValidateInviteCodeView.as_view(), name="validate-invite"),
    url(r'^profession/$', ProfessionListView.as_view(), name="profession"),
    url(r'^skill/$', SkillListView.as_view(), name="skills"),
    url(r'^interest/$', InterestListView.as_view(), name="interests"),
    url(r'^public-feed/$', PublicFeed.as_view()),
    url(r'^me/', include('userprofile.me_urls')),
    url(r'^version/', include('appversion.urls')),

]
