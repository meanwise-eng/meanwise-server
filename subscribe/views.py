from rest_framework.decorators import api_view

from common.http import JsonResponse, JsonErrorResponse

from .models import Invite
from .serializers import InviteSerializer
from .constants import THANK_YOU_FOR_SUBSCRIBING, EMAIL_AREADY_SUBSCRIBED,\
        INVALID_EMAIL, THANK_YOU_FOR_SUBSCRIBING_WITH_USERNAME


@api_view(http_method_names=['POST'])
def request_invite(request):
    data = request.data
    serializer = InviteSerializer(data=data)
    if serializer.is_valid():
        invite = serializer.create(serializer.validated_data)
        if invite.username:
            return JsonResponse({},
                                message=THANK_YOU_FOR_SUBSCRIBING_WITH_USERNAME
                                )
        return JsonResponse({}, message=THANK_YOU_FOR_SUBSCRIBING)
    else:
        return JsonErrorResponse(serializer.errors)
