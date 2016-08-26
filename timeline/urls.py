from django.conf.urls import url
from rest_framework import routers

from .api import EventAPIViewSet, CourseMajorAPIView

router = routers.SimpleRouter()
router.register('events', EventAPIViewSet, 'Event')


urlpatterns = router.urls

urlpatterns += [
    url('^majors/$', CourseMajorAPIView.as_view()),
]
