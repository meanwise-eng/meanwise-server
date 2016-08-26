from django.conf.urls import url

from rest_framework import routers

from .api import (ProfileAPIViewSet, SkillListAPIView, LookingForListAPIView,
                  ProfessionListAPIView, LanguageListAPIView)
from .views import (validate_username, upload_profile_cover_pic, act_on_profile,
                    fetch_relations)

router = routers.SimpleRouter()
router.register('profiles', ProfileAPIViewSet, 'Profile')

urlpatterns = [
    url('^profiles/(?P<pic_type>(upload_profile_pic|upload_cover_pic))/$', upload_profile_cover_pic),
    url('^profiles/(?P<username>[0-9a-z_.]+)/(?P<action>(follow|unfollow|like|unlike))/$', act_on_profile),
    url('^profiles/(?P<username>[0-9a-z_.]+)/(?P<relation_type>(followers|followings|liked_by|likes))/$', fetch_relations),
    url('^skills/$', SkillListAPIView.as_view()),
    url('^languages/$', LanguageListAPIView.as_view()),
    url('^professions/$', ProfessionListAPIView.as_view()),
    url('^lookingFor/$', LookingForListAPIView.as_view()),
    url('^validate_username/', validate_username, name='account_profile_validate_username')
]
urlpatterns += router.urls
