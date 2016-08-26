from rest_framework.decorators import api_view
from rest_framework.response import Response

from common.http import JsonErrorResponse
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN, GENERIC_ERROR_RESPONSE

from .models import Notification


@api_view(http_method_names=['POST'])
def mark_read(request):
    if request.user.is_authenticated():
        profile = request.user.profile
        notif_ids = request.data.get('id')
        if len(notif_ids) > 50:
            return JsonErrorResponse(GENERIC_ERROR_RESPONSE)
        Notification.objects.filter(profile=profile,
                                    id__in=notif_ids).update(read=True)
        Notification.cache.mark_read_bulk(notif_ids, profile)
        return Response(status=204)
    else:
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
