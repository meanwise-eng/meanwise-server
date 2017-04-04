from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import exceptions
from django.shortcuts import render

import logging
import datetime

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import authentication, permissions
from rest_framework.pagination import PageNumberPagination

from mnotifications.models import Notification
from userprofile.models import UserProfile, UserFriend
from post.models import Post, Comment

from mnotifications.serializers import NotificationSerializer
from common.api_helper import get_objects_paginated

logger = logging.getLogger('delighter')

class UserNotificationsNew(APIView):
    """
    List all User notifications that are not notified yet.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        notifications = Notification.objects.filter(was_notified=False).filter(receiver__id=user_id).order_by('-created_on')
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        notifications, has_next_page, num_pages  = get_objects_paginated(notifications, page, page_size)
        serializer = NotificationSerializer(notifications, many=True)
        #set them as notified
        for notification in notifications:
            notification.was_notified = True
            notification.save()
        return Response({"status":"success", "error":"", "results":{"data":serializer.data, "num_pages":num_pages}}, status=status.HTTP_200_OK)

class UserNotificationsLatest(APIView):
    """
    List all User's latest notification, including notified and non notified ones.
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        latest_timestamp = datetime.datetime.now() - datetime.timedelta(hours=24)
        notifications = Notification.objects.filter(created_on__gte=latest_timestamp).filter(receiver__id=user_id).order_by('-created_on')
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        notifications, has_next_page, num_pages  = get_objects_paginated(notifications, page, page_size)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({"status":"success", "error":"", "results":{"data":serializer.data, "num_pages":num_pages}}, status=status.HTTP_200_OK)

