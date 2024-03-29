from django.conf.urls import include, url

from rest_framework import routers

from userprofile.views import *
from post.views import *
from mnotifications.views import *
from credits.views import CreditsListView
from brands.views import OrgListView
from topics.views import TopicsListView

router = routers.SimpleRouter()

# router.register(r'user/userprofile', UserProfileViewSet)
router.register(r'post', PostViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'share', ShareViewSet)

# router.register(r'search/post', PostSearchView, base_name="post-search")
router.register(r"search/userprofile", UserProfileSearchView,
                base_name="userprofile-search")
router.register(r'autocomplete/profession',
                ProfessionSearchView, base_name="profession-search")
router.register(r'autocomplete/skill', SkillSearchView,
                base_name="skill-search")
router.register(r'autocomplete/user', UserMentionAutoComplete,
                base_name="user-autocomplete")

urlpatterns = [
    url(r'custom_auth/', include('custom_auth.urls')),
    url(r'^', include(router.urls, namespace="route")),
    url(r'^user/userprofile/$', UserProfileList.as_view(),
        name="profile-list"),
    url(r'^user/by-username/(?P<username>[^/]+)/userprofile/$',
        UserProfileDetailByUsername.as_view(), name="profile-detail-by-username"),
    url(r'^user/(?P<user_id>[0-9]+)/userprofile/$',
        UserProfileDetail.as_view(), name="profile-detail"),
    url(r'^user/(?P<user_id>[0-9]+)/change/password/$',
        ChangePasswordView.as_view(), name="change-password"),
    url(r'^user/forgot/password/$',
        ForgotPasswordView.as_view(), name="forget-password"),
    # url(r'^user/(?P<user_id>[0-9]+)/friend-request/$',
    #     FriendRequestView.as_view(), name="friend-request"),
    url(r'^user/(?P<user_id>[0-9]+)/friends/$',
        FriendsList.as_view(), name='friends'),
    url(r'^user/(?P<user_id>[0-9]+)/friends/remove/$',
        RemoveFriend.as_view(), name="remove-friend"),
    url(r'^user/(?P<user_id>[0-9]+)/posts/$',
        UserPostList.as_view(), name="post-list"),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[0-9]+)/$',
        UserPostDetail.as_view(), name="post-detail"),
    url(r'^user/(?P<user_id>[0-9]+)/friends/posts/$',
        UserFriendsPostList.as_view(), name="friend-post"),
    url(r'^user/(?P<user_id>[0-9]+)/interests/posts/$',
        UserInterestsPostList.as_view(), name="interest-post"),
    url(r'^user/(?P<user_id>[0-9]+)/home/feed/$',
        UserHomeFeed.as_view(), name="home-feed"),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[a-z0-9-]+)/like/$',
        UserPostLike.as_view(), name="post-like"),
    url(r'^user/(?P<user_id>[0-9]+)/posts/(?P<post_id>[0-9]+)/unlike/$',
        UserPostUnLike.as_view(), name="post-unlike"),
    url(r'^user/(?P<user_id>[0-9]+)/user-topics/',
        UserTopicsListView.as_view(), name='user-topics'),
    url(r'^user/(?P<user_id>[0-9]+)/credits/',
        CreditsListView.as_view(), name='user-credits'),
    url(r'^story/(?P<story_id>[0-9]+)/',
        StoryDetail.as_view(), name='post-story'),
    url(r'^posts/', include('post.urls')),
    url(r'^search/post/$', PostExploreView.as_view(), name='post-search'),
    url(r'^interests/(?P<interest_id>[0-9]+)/topics/trending/$',
        TrendingTopicForInterest.as_view()),
    url(r'^topics/trending/$',
        TrendingTopics.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/notifications/new/$',
        UserNotificationsNew.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/notifications/latest/$',
        UserNotificationsLatest.as_view()),
    url(r'^amazon/notification/device/register/$',
        AmazonNotificationAddDevice.as_view()),
    url(r'^amazon/notification/device/delete/$',
        AmazonNotificationDeleteDevice.as_view()),
    url(r'^amazon/notification/message/send/$',
        AmazonNotificationSendMessage.as_view()),
    url(r'^invite/code/valid/$',
        ValidateInviteCodeView.as_view(), name="validate-invite"),
    url(r'^profession/$', ProfessionListView.as_view(), name="profession"),
    url(r'^skill/$', TopicsListView.as_view(), name="skills"),
    url(r'^interest/$', InterestListView.as_view(), name="interests"),
    url(r'^public-feed/$', PublicFeed.as_view(), name="public-feed"),
    url(r'^subscribe/early-access/', EarlyAccess.as_view()),
    url(r'^explore-orgs/$', OrgListView.as_view()),
    url(r'^me/', include('userprofile.me_urls')),
    url(r'^version/', include('appversion.urls')),
    url(r'^analytics/', include('analytics.urls')),
    url(r'^discussions/', include('discussions.urls')),
    url(r'^influencers/$', InfluencersListView.as_view()),
    url(r'^brands/', include('brands.urls')),
    url(r'^college/', include('college.urls')),
    url(r'^media/', include('mwmedia.urls')),
]
