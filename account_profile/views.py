from django.db.models import ObjectDoesNotExist
from django.db import IntegrityError

from rest_framework.decorators import api_view
from rest_framework.response import Response

from common.http import JsonErrorResponse
from common.forms import ImageUploadForm
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN, GENERIC_ERROR_RESPONSE

from .models import Profile, CoverImage, ProfileImage
from .serializers import ValidateUsernameSerializer, DefaultProfileDetailSerializer
from .constants import PROFILE_NOT_FOUND

@api_view(http_method_names=['POST'])
def validate_username(request):
    if request.user.is_authenticated():
        serializer = ValidateUsernameSerializer(data=request.data)
        if serializer.is_valid():
            response = Response(serializer.validated_data)
        else:
            response = JsonErrorResponse(serializer.errors)
        return response
    else:
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)

@api_view(http_method_names=['POST'])
def upload_profile_cover_pic(request, pic_type):
    if request.user.is_authenticated():
        profile = request.user.profile
        if pic_type == 'upload_profile_pic':
            image = ProfileImage(image=request.FILES['image'])
            image.save()
            profile.profile_photo = image
            profile.save()
            response = {'profile': {'profilePhoto': profile.profile_photo_url}}
        elif pic_type == 'upload_cover_pic':
            image = CoverImage(image=request.FILES['image'])
            image.save()
            profile.cover_photo = image
            profile.save()
            response = {'profile': {'coverPhoto': profile.cover_photo_url}}
        return Response(response)
    else:
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)

@api_view(http_method_names=['POST'])
def act_on_profile(request, username, action):
    if request.user.is_authenticated():
        profile = request.user.profile
        if profile.username == username or profile.id == username:
            pass
        else:
            try:
                target_profile = Profile.objects.get_by_username_id(username)
            except ObjectDoesNotExist as e:
                return JsonErrorResponse(PROFILE_NOT_FOUND, status=404)

            try:
                method = getattr(Profile.objects, action)
                method(profile, target_profile)
            except IntegrityError as e:
                pass
            except Exception as e:
                return JsonErrorResponse(GENERIC_ERROR_RESPONSE)
        return Response()
    else:
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)

@api_view(http_method_names=['GET'])
def fetch_relations(request, username, relation_type):
    if relation_type not in  ['followers', 'followings'] and not request.user.is_authenticated():
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
    try:
        profile = Profile.objects.get_by_username_id(username)
    except ObjectDoesNotExist as e:
        return JsonErrorResponse(PROFILE_NOT_FOUND, status=404)
    try:
        profiles = getattr(profile, relation_type)
    except IntegrityError as e:
        return JsonErrorResponse(GENERIC_ERROR_RESPONSE)
    profile_data = []
    for p in profiles:
        profile_data.append(Profile.cache.serialized(p, DefaultProfileDetailSerializer))
    return Response({'profile': profile_data})
