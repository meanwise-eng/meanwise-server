from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from .models import Activity
from .serializers import NotificationSerializer


class NotificationAPIView(ListAPIView):
    '''
    This class is responsible for fetching notifications for a profile.
    Notifications should be paginated.
    '''

    def get(self, request):
        if request.user.is_authenticated():
            profile = request.user.profile
            activities = Activity.objects.by_target(profile)
            serializer = NotificationSerializer(activities, many=True)
            return Response({'notifications': serializer.data})
        else:
            return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
