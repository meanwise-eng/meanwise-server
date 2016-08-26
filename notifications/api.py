from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from common.http import JsonErrorResponse
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN

from .models import Notification
from .serializers import NotificationSerializer


class NotificationAPIView(ListAPIView):
    '''
    This class is responsible for fetching notifications for a profile.
    Notifications should be paginated.
    '''
    MAX_COUNT = 10

    def get(self, request):
        if request.user.is_authenticated():
            profile = request.user.profile
            count = min(int(request.query_params.get('count', 10)),
                        self.MAX_COUNT)
            since = request.query_params.get('since')
            since = int(since) if since else None
            till = request.query_params.get('till')
            till = int(till) if till else None

            if since and Notification.cache.last_added_by_profile(profile) <= since:
                notifications = []
            else:
                notifications = Notification.cache.get_by_profile(profile,
                                                                  count,
                                                                  since, till)
                if not notifications:
                    Notification.cache.build(profile)
                    notifications = Notification.cache.get_by_profile(profile,
                                                                      count,
                                                                      since,
                                                                      till)
            return Response({'notifications': notifications})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
