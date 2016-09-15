from django.http import HttpRequest
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from requests.exceptions import HTTPError

from userprofile.models import Profession, Skill, Interest, UserProfile

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile

    