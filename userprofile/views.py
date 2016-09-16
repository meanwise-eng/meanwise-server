from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from userprofile.models import Profession, Skill, Interest, UserProfile
from userprofile.serializers import *


class ProfessionViewSet(viewsets.ModelViewSet):
    """
    Profession apis

    """
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'text', 'slug', 'created_on', 'last_updated', 'searchable')


class SkillViewSet(viewsets.ModelViewSet):
    """
    Skill apis

    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'text', 'lower', 'slug',
              'created_on', 'last_updated', 'searchablge')


class InterestViewSet(viewsets.ModelViewSet):
    """
    Interest apis

    """
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'name', 'slug', 'description',
              'created_on', 'modified_on', 'published',
              'cover_photo', 'color_code')


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    UserProfile apis

    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    fields = ('id', 'username', 'first_name', 'middle_name',
              'last_name', 'profession', 'city', 'skills',
              'interests', 'profile_photo', 'cover_photo',
              'bio', 'created_on', 'last_updated')
