from django.conf.urls import url

from rest_framework_nested import routers

from .views import like_unlike_work, add_image_type_workitem
from .api import WorkAPIViewSet, WorkitemAPIViewSet, CommentAPIViewSet

router = routers.SimpleRouter()
router.register('works', WorkAPIViewSet, 'Work')

workitem_router = routers.NestedSimpleRouter(router, 'works', lookup='work')
workitem_router.register('workitems', WorkitemAPIViewSet, 'Workitem')
comment_router = routers.NestedSimpleRouter(router, 'works', lookup='work')
comment_router.register('comments', CommentAPIViewSet, 'Comment')

urlpatterns = [
    url('^works/(?P<work_id>[0-9]+)/(?P<action>(like|unlike))/$',
        like_unlike_work),
    url('^works/(?P<work_id>[0-9]+)/workitems/image/$',
        add_image_type_workitem),
]

urlpatterns += router.urls
urlpatterns += workitem_router.urls
urlpatterns += comment_router.urls
