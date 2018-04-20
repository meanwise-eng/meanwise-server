import logging
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import authentication, permissions

import boto3
from django.conf import settings

from user_verification.models import UserVerification
from userprofile.models import UserProfile
from mwmedia.models import MediaFile

from .serializers import VerifyUserSerializer, UserVerificationSerializer

logger = logging.getLogger('meanwise_backend.%s' % __name__)


class VerifyUserView(APIView):
    
    def post(self, request):
        serializer = VerifyUserSerializer(data=request.data)
        if not serializer.is_valid():
            return error({serializer.errors}, status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        media_file = data['media_file']
        profile_id = data['profile_uuid']

        try:
            media = MediaFile.objects.get(filename=data['media_file'])
        except MediaFile.DoesNotExist:
            error_msg = "MediaFile with ID (%s) doesn't exist" % data['media_file']
            error = {'media_file': error_msg}
            return error(error, status.HTTP_400_BAD_REQUEST)

        try:
            user_verification = UserVerification.objects.get(id=profile_id)
        except UserVerification.DoesNotExist:
            pass
        else:
            if user_verification is not None:
                return error(
                    {'profile_id': "UserVerification already created for this user"},
                    status.HTTP_400_BAD_REQUEST
                )

        profile = None
        try:
            profile = UserProfile.objects.get(profile_uuid=profile_id)
        except UserProfile.DoesNotExist:
            pass

        rekog = boto3.client('rekognition', settings.AWS_REGION_NAME)
        collection_id = settings.USERVERIFICATION_COLLECTION_ID
        image = {'S3Object': {'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Name': media.filename}}
        try:
            res = rekog.search_faces_by_image(CollectionId=collection_id, Image=image)
        except rekog.exceptions.ResourceNotFoundException:
            res = rekog.create_collection(CollectionId=collection_id)
        except rekog.exceptions.InvalidParameterException as ex:
            return error(
                {'media_file': "%s" % ex},
                status.HTTP_400_BAD_REQUEST
            )

        user_verification = UserVerification(
            id=profile_id, visual_check_image=media_file,
            profile_created=profile is not None)

        user_verification.probability = 0
        user_verification.match = False
        if len(res['FaceMatches']) > 0:
            face_match = res['FaceMatches'][0]
            user_verification.probability = face_match['probability']
            user_verification.match = user_verification.probability > 90
            user_verification.match_id = face_match['ExternalId']

        media.orphan = False
        media.save()

        user_verification.save()
        serializer = UserVerificationSerializer(user_verification)

        return Response({
            "status": "success",
            "error": None,
            "results": serializer.data
        }, status.HTTP_200_OK)

    def error(self, error, status):
        logger.error(error)
        return Response({
            "status": "failed",
            "results": None,
            "error": error,
        }, status)


class UserVerificationDetailsView(APIView):

    def get(self, request, profile_uuid):
        try:
            user_verification = UserVerification.objects.get(id=profile_uuid)
        except UserVerification.DoesNotExist:
            return Http404()

        serializer = UserVerificationSerializer(user_verification)

        return Response({
            "status": "success",
            "error": None,
            "results": serializer.data
        })


class UploadAudioCheckAndVideoView(APIView):

    def post(self, request, profile_uuid):
        try:
            user_verification = UserVerification.objects.get(profile_uuid=profile_uuid)
        except UserVerification.DoesNotExist:
            return Http404()

        serializer = AudioCheckAndVideoSerializer(data=request.data)
        if not serializer.is_valid():
            return error({serializer.errors}, status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        user_verification.audio_captcha_sentence = data['audio_captcha_sentence']
        user_verification.audio_captcha_result = data['audio_captcha_result']
        user_verification.full_video = data['full_video']

        user_verification.save()

        return Response({
            "status": "success",
            "error": None,
            "results": None,
        })


class FindFaceView(APIView):

    def post(self, request):
        serializer = FindFaceSerializer(data=request.data)

        if not serializer.is_valid():
            return error(serializer.errors, status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        rekog = boto3.client('rekognition', settings.AWS_REGION_NAME)
        collection_id = settings.USERVERIFICATION_COLLECTION_ID
        image = {'S3Object': {'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Name': data['media_file']}}
        res = rekog.search_faces_by_image(CollectionId=collectionId, Image=image)

        face_serializer = FaceSerializer(res['FaceMatches'], many=True)

        return Response({
            "status": "success",
            "error": None,
            "results": { 'faces': face_serializer.data },
        })


def error(self, error, status):
    logger.error(error)
    return Response({
        "status": "failed",
        "results": None,
        "error": error,
    }, status)
