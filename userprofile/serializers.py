from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from easy_thumbnails.files import get_thumbnailer

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
    user_id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    profession = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    profile_photo_small = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'email', 'username', 'profile_photo', 'cover_photo', 'profile_photo_small', 'first_name', 'last_name', 'bio',
                      'skills', 'profession', 'interests']

    def get_user_id(self, obj):
        user_id = obj.user.id
        return user_id

    def get_email(self, obj):
        email = obj.user.email
        return email

    def get_profile_photo_small(self, obj):
        small = {'size': (48, 48), 'crop': True}
        profile_photo_small_url = ""
        if obj.profile_photo:
            profile_photo_small_url = get_thumbnailer(obj.profile_photo).get_thumbnail(small).url
        return profile_photo_small_url

    def get_skills(self, obj):
        skills = obj.skills.all()
        skills_list = []
        for skill in skills:
            data ={
                'name': skill.text,
                'id': skill.id,
                }
            skills_list.append(data)
        return skills_list

    def get_profession(self, obj):
        profession = obj.profession
        data = {}
        if profession:
            data = {
                'name': profession.text,
                'id': profession.id,
                }
        return data


    def get_interests(self, obj):
        interests = obj.interests.all()
        interests_list = []
        for interest in interests:
            data ={
                'name': interest.name,
                'id': interest.id,
                }
            interests_list.append(data)
        return interests_list