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
        register_data = request.data
        reg_user_serializer = RegisterUserSerializer(data=register_data)
        if reg_user_serializer.is_valid():
            user, user_profile, auth_token = reg_user_serializer.save()
            response_user_data = {}
            response_user_data['auth_token'] = auth_token
            response_user_data['user'] = user.id
            response_user_data['userprofile'] = user_profile.id
            response_data = {'status':'success', 'error':'', 'results':response_user_data}
            logger.info("RegisterUserView - POST - Finished ")
            
            return Response(response_data, status=status.HTTP_201_CREATED)

        logger.error("RegisterUserView - POST - Invalid Serializer")
        
        return Response({'status':'failed','error':reg_user_serializer.errors, 'data':''},
                        status=status.HTTP_400_BAD_REQUEST)


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

    return Response({'status':'success', 'error':'', 'results':response_data}, status=status.HTTP_202_ACCEPTED)


class FetchToken(APIView):
    permission_classes = (AllowAny,)

    @csrf_exempt
    def post(self, request):
        logger.info("Request for FetchToken POST - Fetch token API / views.py /")
        try:
            email = request.data.get('email', None)
            password = request.data.get('password', None)
            facebook_token = request.data.get('facebook_token', None)
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"status":"failed", "error":"User with email does not exist", "results":""}, status.HTTP_400_BAD_REQUEST)

            if password:
                #check password
                isvalid = user.check_password(password)
                if not isvalid:
                    return Response({"status":"failed", "error":"User password did not match", "results":""}, status.HTTP_400_BAD_REQUEST)
            elif facebook_token:
                try:
                    up = UserProfile.objects.get(user=user)
                except UserProfile.DoesNotExist:
                    return Response({"status":"failed", "error":"UserProfile for user not found", "results":""}, status.HTTP_400_BAD_REQUEST)
                if facebook_token !=  up.facebook_token:
                    return Response({"status":"failed", "error":"User fb token did not match", "results":""}, status.HTTP_400_BAD_REQUEST)
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                return Response({"status":"failed", "error":"Token for User with email does not exist", "results":""}, status.HTTP_400_BAD_REQUEST)
            data = {"token":token.key, "user_id":user.id}

            return Response({"status":"success", "error":"", "result":data} ,  status.HTTP_200_OK)
                                    
        except Exception as e:
            logger.error("Fetch Token - POST - Exception: " + e.message + " [API / views.py /")
            return Response({"status":"failed", "error":str(e), "results":""}, status.HTTP_400_BAD_REQUEST)

