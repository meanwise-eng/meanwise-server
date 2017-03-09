from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from easy_thumbnails.files import get_thumbnailer

from drf_haystack.serializers import HaystackSerializerMixin

from userprofile.models import *
from django.contrib.auth.models import User

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ('id', 'text')

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'text')


class InterestSerializer(TaggitSerializer, serializers.ModelSerializer):
    #topics = TagListSerializerField()
    photo = serializers.SerializerMethodField()
    class Meta:
        model = Interest
        fields = ('id', 'name', 'photo')

    def get_photo(self, obj):
        if obj.cover_photo:
            photo_url = obj.cover_photo.url
            return photo_url
        return ""
    
class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    user_profession = serializers.SerializerMethodField()
    user_interests = serializers.SerializerMethodField()
    profile_photo_small = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    user_friends = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'email', 'username', 'profile_photo', 'cover_photo', 'profile_photo_small', 'first_name', 'last_name', 'bio',
                      'skills', 'profession', 'user_profession', 'interests', 'user_interests', 'intro_video', 'phone', 'dob', 'profile_story_title', 'profile_story_description', 'city',
                      'user_friends']

    def get_user_id(self, obj):
        user_id = obj.user.id
        return user_id

    def get_email(self, obj):
        email = obj.user.email
        return email

    def get_username(self, obj):
        username = obj.user.username
        return username

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

    def get_user_profession(self, obj):
        profession = obj.profession
        data = {}
        if profession:
            data = {
                'name': profession.text,
                'id': profession.id,
                }
        return data


    def get_user_interests(self, obj):
        interests = obj.interests.all()
        interests_list = []
        for interest in interests:
            data ={
                'name': interest.name,
                'id': interest.id,
                }
            interests_list.append(data)
        return interests_list

    def get_user_friends(self, obj):
        ufs = UserFriend.objects.filter(user=obj.user)
        ufs_list = []
        for uf in ufs:
            data ={
                'friend_id':uf.friend.id,
                'friend_name': uf.friend.username,
                'friend_email': uf.friend.email,
                'status':uf.get_status_display()
                }
            ufs_list.append(data)
        return ufs_list

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'userprofile')

class UserFriendSerializer(serializers.ModelSerializer):
    friend = UserSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'friend')
        
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class UserProfileSearchSerializer(HaystackSerializerMixin, UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        search_fields = ("text", "userprofile_id", "first_name", "last_name", "username", "skills_text", 'created_on')