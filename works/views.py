from django.conf import settings
from django.db.models import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response


from common.http import JsonErrorResponse
from common.serializers import CommentSerializer
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN

from .models import Work, Workitem
from .forms import WorkCoverPictureUploadForm
from .serializers import WorkSerializer, WorkitemSerializer
from .utils import handle_workitem_image_upload
from .constants import WorkItemType, WORK_NOT_FOUND

@api_view(http_method_names=['POST'])
def like_unlike_work(request, work_id, action):
    if not request.user.is_authenticated():
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN)

    profile = request.user.profile
    try:
        work = Work.objects.published().get(pk=work_id)
    except ObjectDoesNotExist as e:
        return JsonErrorResponse(WORK_NOT_FOUND)

    getattr(Work.objects, action)(work, profile)
    return Response(status=204)


@api_view(http_method_names=['POST'])
def add_image_type_workitem(request, work_id):
    if not request.user.is_authenticated():
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN)
    profile = request.user.profile
    try:
        work = Work.objects.get(pk=work_id, profile=profile)
    except ObjectDoesNotExist as e:
        return JsonErrorResponse(WORK_NOT_FOUND)
    # Using same for image type workitem
    form = WorkCoverPictureUploadForm(request.POST, request.FILES)
    if form.is_valid():
        url = settings.MEDIA_URL + handle_workitem_image_upload(request.FILES['picture'])
        workitem = Workitem(link=url, work=work, type=WorkItemType.IMAGE)
        workitem.save()
        return Response({'workitem': WorkitemSerializer(workitem).data})
    else:
        print (form.errors)
        return JsonErrorResponse(form.errors)
