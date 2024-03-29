from django.conf import settings
from django.contrib.auth.models import User

import logging
import datetime

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import authentication, permissions

from mnotifications.models import Notification, ASNSDevice

from mnotifications.serializers import NotificationSerializer
from common.api_helper import get_objects_paginated

from scarface.models import *

logger = logging.getLogger('delighter')


class UserNotificationsNew(APIView):
    """
    List all User notifications that are not notified yet.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        notifications = Notification.objects.filter(was_notified=False).filter(
            receiver__id=user_id).order_by('-created_on')
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        notifications, has_next_page, num_pages = get_objects_paginated(
            notifications, page, page_size)
        serializer = NotificationSerializer(notifications, many=True, context={request: request})
        # set them as notified
        for notification in notifications:
            notification.was_notified = True
            notification.save()
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    "num_pages": num_pages
                }
            },
            status=status.HTTP_200_OK
        )


class UserNotificationsLatest(APIView):
    """
    List all User's latest notification, including notified and non notified ones.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        latest_timestamp = datetime.datetime.now() - datetime.timedelta(weeks=3)
        notifications = Notification.objects.filter(created_on__gte=latest_timestamp).filter(
            receiver__id=user_id).order_by('-created_on')
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        notifications, has_next_page, num_pages = get_objects_paginated(
            notifications, page, page_size)
        serializer = NotificationSerializer(notifications, many=True, context={request: request})
        return Response(
            {
                "status": "success",
                "error": "",
                "results": {
                    "data": serializer.data,
                    "num_pages": num_pages
                }
            },
            status=status.HTTP_200_OK
        )


class AmazonNotificationAddDevice(APIView):
    """
    Add device to send message
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            app = Application.objects.get(name=settings.AMAZON_SNS_APP_NAME)
        except Application.DoesNotExist:
            return Response({"status": "failed", "error": "No Amazon sns app found.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)
        try:
            topic = Topic.objects.get(name=settings.AMAZON_SNS_TOPIC_NAME)
        except Topic.DoesNotExist:
            return Response({"status": "failed", "error": "No Amazon sns topic found.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)

        device_id = request.data.get('device_id', '')
        if not device_id:
            return Response({"status": "failed", "error": "No device_id provided.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)
        device_token = request.data.get('device_token', '')
        if not device_token:
            return Response({"status": "failed", "error": "No device_token provided.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.data.get('user_id', '')
        if not user_id:
            return Response({"status": "failed", "error": "No user_id provided.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=int(user_id))
        except User.DoesNotExist:
            Response({"status": "failed", "error": "User with user_id does not exist.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)

        platform = request.data.get('platform', 'APNS')
        if platform == 'APNS':
            p_name = settings.AMAZON_SNS_PLATFORM_APNS
        elif platform == 'GCM':
            p_name = settings.AMAZON_SNS_PLATFORM_GCM
        else:
            p_name = platform
        try:
            platform = Platform.objects.get(platform=p_name)
        except Platform.DoesNotExist:
            Response({"status": "failed", "error": "No Platform found.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ASNSDevice.objects.filter(device__device_id=device_id).delete()
        except Exception as e:
            return Response(
                {
                    "status": "failed",
                    "error": str(e),
                    "results": "Could not delete existing ASNSdevice record"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        device = None
        # register device with platform and topic
        try:
            device = Device.objects.get(device_id=device_id, push_token=device_token,
                                        platform=platform)
        except Device.DoesNotExist:
            Device.objects.filter(device_id=device_id, platform=platform).delete()
            Device.objects.filter(push_token=device_token, platform=platform).delete()
            device = Device.objects.create(device_id=device_id, push_token=device_token,
                                           platform=platform)

        try:
            ASNSDevice.objects.create(device=device, user=user)
            device.register()
            topic.register_device(device)
        except Exception as e:
            return Response(
                {
                    "status": "failed",
                    "error": str(e),
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "status": "success",
                "error": "",
                "results": "Successfully registered the device"
            },
            status=status.HTTP_201_CREATED
        )


class AmazonNotificationDeleteDevice(APIView):
    """
    Delete device
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        device_id = request.data.get('device_id', '')
        if not device_id:
            Response({"status": "failed", "error": "No device_id provided.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            Response({"status": "failed", "error": "No device found.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)

        # register device with platform and topic
        try:
            device.delete()
        except Exception as e:
            return Response(
                {
                    "status": "failed",
                    "error": str(e),
                    "results": ""
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ASNSdevice = ASNSDevice.objects.get(device__device_id=device_id)
            if ASNSdevice:
                ASNSdevice.delete()
        except ASNSDevice.DoesNotExist:
            pass
        return Response(
            {
                "status": "success",
                "error": "",
                "results": "Successfully deleted the device"
            },
            status=status.HTTP_201_CREATED
        )


class AmazonNotificationSendMessage(APIView):
    """
    Send message
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            topic = Topic.objects.get(name=settings.AMAZON_SNS_TOPIC_NAME)
        except Topic.DoesNotExist:
            Response({"status": "failed", "error": "No Amazon sns topic found.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)

        device_ids = request.data.get('device_ids', '')
        message = request.data.get('message', '')
        if not message:
            Response({"status": "failed", "error": "No message provided.",
                      "results": ""}, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = PushMessage(badge_count=1, context='url_alert', context_id='none',
                                  has_new_content=True,
                                  message='test sns push notification, aas mobile',
                                  sound="default")
        except Exception as e:
            Response({"status": "failed", "error": str(e), "results": ""},
                     status=status.HTTP_400_BAD_REQUEST)

        if not device_ids:
            # send message to all
            try:
                topic.send(message)
            except Exception as e:
                return Response(
                    {
                        "status": "failed",
                        "error": str(e),
                        "results": "Could not send message to all"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif device_ids:
            for device in device_ids:
                try:
                    device = Device.objects.get(device_id=device_id)
                    device.send(message)
                except Exception as e:
                    return Response(
                        {
                            "status": "failed",
                            "error": str(e),
                            "results": "Could not send message to device"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(
            {
                "status": "success",
                "error": "",
                "results": "Successfully sent message"
            },
            status=status.HTTP_201_CREATED
        )
