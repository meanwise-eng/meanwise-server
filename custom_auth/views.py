from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import logging

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from custom_auth.serializers import *

logger = logging.getLogger('meanwise')

class RegisterUserView(APIView):
    """
    Handle Registering of user for both normal django flow and facebook flow.
    Capture all user information at one go.
    For each user generate auth token and use the same to authorize further api calls.
    
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        logger.info("RegisterUserView - POST ")
        register_data = request.data.get('register')
        reg_user_serializer = RegisterUserSerializer(data=register_data)
        if reg_user_serializer.is_valid():
            user, user_profile, auth_token = reg_user_serializer.save()
            response_data = {}
            response_data['auth_token'] = auth_token
            response_data['user'] = user.id
            response_data['userprofile'] = user_profile.id
            logger.info("RegisterUserView - POST - Finished ")
            return Response(response_data, status=status.HTTP_201_CREATED)

        logger.error("RegisterUserView - POST - Invalid Serializer")
        return Response(reg_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_user(request):
    """
    Check if user with given email exists

    """
    email = request.data.get('email', None)
    exists = False
    if email:
        try:
            user = User.objects.get(email=email)
            exists = True
        except User.DoesNotExist:
            pass
    response_data = {}
    if exists:
        response_data['exists'] = 'true'
    else:
        response_data['exists'] = 'false'
        
    return Response(response_data, status=status.HTTP_202_ACCEPTED)