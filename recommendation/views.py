from django.db.models import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.decorators import api_view

from account_profile.models import Profile
from account_profile.serializers import SimilarProfileDetailSerializer
from common.http import JsonErrorResponse
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN, GENERIC_ERROR_RESPONSE

from .utils import get_profile_hits_recommendations, get_similar_profiles


@api_view(http_method_names=['GET'])
def profile_hit_recommendations(request):
    if not request.user.is_authenticated():
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)

    profiles = get_profile_hits_recommendations(request.user.profile)
    serializer = SimilarProfileDetailSerializer(profiles, many=True)
    return Response({'profile': serializer.data})


@api_view(http_method_names=['GET'])
def similar_profiles(request):
    if request.user.is_authenticated():
        logged_in_profile = request.user.profile
    else:
        logged_in_profile = None
    username = request.query_params.get('username', '')
    if not username:
        return JsonErrorResponse(GENERIC_ERROR_RESPONSE)
    try:
        profile = Profile.objects.get_by_username_id(username)
    except ObjectDoesNotExist as e:
        return Response({'profile': []})
    similar_profiles = get_similar_profiles(profile, logged_in_profile)
    serializer = SimilarProfileDetailSerializer(similar_profiles, many=True)
    return Response({'profile': serializer.data})
