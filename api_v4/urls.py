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

urlpatterns = [
    url(r'custom_auth/', include('custom_auth.urls')),
    url(r'^', include(router.urls)),
]
