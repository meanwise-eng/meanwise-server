from rest_framework import serializers

from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer

from userprofile.models import Profession, Skill, Interest, UserProfile


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill


class InterestSerializer(TaggitSerializer, serializers.ModelSerializer):
    topics = TagListSerializerField()
    class Meta:
        model = Interest


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
