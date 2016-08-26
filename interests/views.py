from django.shortcuts import render
from django.db.models import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response

from account_profile.models import Profile, post_profile_save
from common.http import JsonErrorResponse
from common.constants import UNAUTHENTICATED_NOT_LOGGEDIN

from .models import Interest


@api_view(http_method_names=['POST'])
def follow_unfollow_interest(request, interest_id, action):
    '''
    This function is used to follow/unfollow interests.
    User's can follow or unfollow multiple interests.
    In case of multiple follows, first existing ones are deleted and
    repopulated with new values. Rest works as expected.
    '''
    user = request.user
    if user.is_authenticated():
        profile = user.profile
        try:
            interest = Interest.objects.get(id=interest_id)
        except ObjectDoesNotExist as e:
            return JsonErrorResponse(e)
        if not interest.published:
            return JsonErrorResponse('Invalid interest')
        if action == 'follow':
            profile.interests.add(interest)
        elif action == 'unfollow':
            profile.interests.remove(interest)
        post_profile_save(Profile, profile)
        return Response()
    else:
        # TODO Need better way of implementing this
        return JsonErrorResponse(UNAUTHENTICATED_NOT_LOGGEDIN, status=401)
