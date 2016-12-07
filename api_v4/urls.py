from django.conf.urls import include, url

from rest_framework import routers
router = routers.SimpleRouter()

from userprofile.views import *
from post.views import *

router.register(r'profession', ProfessionViewSet)
router.register(r'skill', SkillViewSet)
router.register(r'interest', InterestViewSet)
router.register(r'user/userprofile', UserProfileViewSet)
router.register(r'post', PostViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'share', ShareViewSet)

router.register("post/search", PostSearchView, base_name="post-search")
router.register("userprofile/search", UserProfileSearchView, base_name="userprofile-search")

urlpatterns = [
    url(r'custom_auth/', include('custom_auth.urls')),
    url(r'^', include(router.urls)),
    url(r'^user/(?P<user_id>[0-9]+)/friends$', FriendsList.as_view()),
    url(r'^user/(?P<user_id>[0-9]+)/friends/remove$', RemoveFriend.as_view()),
]
