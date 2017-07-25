from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from django.db.models import Q
from django.urls import reverse

import logging
import ast

from drf_haystack.serializers import HaystackSerializerMixin, HaystackSerializer

from userprofile.models import *
from django.contrib.auth.models import User
from userprofile.search_indexes import UserProfileIndex, ProfessionIndex, SkillIndex

logger = logging.getLogger('meanwise_backend.%s' % __name__)

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

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    user_skills = serializers.SerializerMethodField()
    user_profession = serializers.SerializerMethodField()
    user_interests = serializers.SerializerMethodField()
    profile_photo_small = serializers.ImageField(source='profile_photo_thumbnail')
    username = serializers.SerializerMethodField()
    user_username = serializers.CharField(required=False, max_length=100, allow_blank=True)
    user_type = serializers.IntegerField(read_only=True)
    friend_request_status = serializers.SerializerMethodField(read_only=True)
    friends_url = serializers.SerializerMethodField(read_only=True)
    friend_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'email', 'username', 'user_username', 'profile_photo', 'cover_photo', 'profile_photo_small', 'first_name', 'last_name', 'bio',
                      'user_skills', 'skills', 'profession', 'user_profession', 'interests', 'user_interests', 'intro_video', 'phone', 'dob', 'profile_story_title', 'profile_story_description', 'city',
                      'profession_text', 'skills_list', 'profile_background_color', 'user_type',
                      'friend_request_status', 'friends_url', 'friend_count',]

    def get_user_id(self, obj):
        user_id = obj.user.id
        return user_id

    def get_email(self, obj):
        email = obj.user.email
        return email

    def get_username(self, obj):
        username = obj.user.username
        return username

    def get_user_skills(self, obj):
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

    def get_friend_request_status(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            request = self.context.get('request')
            if not request or not hasattr(request, 'user'):
                return None

            if not request.user.id:
                return None

            user_id = request.user.id

        try:
            friend_request = UserFriend.objects.get(
                Q(
                    Q(user_id=user_id) & Q(friend_id=obj.user.id)
                ) | # or
                Q(
                    Q(friend_id=user_id) & Q(user_id=obj.user.id)
                )
            )
        except UserFriend.DoesNotExist:
            return None

        return friend_request.get_status_display()

    def get_friends_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        return request.build_absolute_uri(reverse('friends-list', args=[obj.user.id]))

    def get_friend_count(self, obj):
        user_id = self.context.get('user_id')

        if not user_id:
            request = self.context.get('request')
            if not request or not hasattr(request, 'user'):
                return 0

            if not request.user.id:
                return 0

            user_id = request.user.id

        try:
            friend_count = UserFriend.objects\
                .filter(Q(Q(user_id=user_id) | Q(friend_id=obj.user.id)))\
                .filter(status=UserFriend.STATUS_ACCEPTED)
        except UserFriend.DoesNotExist:
            return 0

        return friend_count.count()

    def update(self, obj, validated_data):
        super().update(obj, validated_data)

        skills_list_from_skills = list()

        if 'skills' in validated_data:
            skills = validated_data.get('skills', None)
            if skills == None:
                UserProfile.skills.through.objects.filter(userprofile_id=obj.id).delete()
            else:
                skills_list_from_skills = [skill.text for skill in skills]

        if 'skills_list' in validated_data:
            skills_list = validated_data.get('skills_list', list())
            logger.info("Skills list: %s of type %s" % (skills_list, type(skills_list)))

            if type(skills_list) == str or type(skills_list) == int:
                skills_list = list(skills_list)
            if len(skills_list) > 0 and type(skills_list[0]) == str and skills_list[0].find('[') != -1:
                skills_list = ast.literal_eval(skills_list[0])

            for skill_text in skills_list:
                if skill_text in skills_list_from_skills:
                    continue

                try:
                    skill = Skill.objects.get(text=skill_text)
                    obj.skills.add(skill)
                except Skill.DoesNotExist:
                    pass
            obj.skills_list = list(set(skills_list + skills_list_from_skills))

        obj.save()
        return obj

class UserProfileSerializer(UserProfileUpdateSerializer):

    class Meta(UserProfileUpdateSerializer.Meta):
        fields = ['id', 'user_id', 'email', 'username', 'user_username', 'profile_photo',
            'cover_photo', 'profile_photo_small', 'first_name', 'last_name', 'bio', 'user_skills',
            'skills', 'profession', 'user_profession', 'interests', 'user_interests',
            'intro_video', 'phone', 'dob', 'profile_story_title', 'profile_story_description',
            'city', 'profession_text', 'skills_list', 'user_type',
            'profile_background_color', 'friend_request_status', 'friends_url', 'friend_count',
        ]

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'userprofile')

class UserFriendSerializer(serializers.ModelSerializer):
    friend = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'friend', 'user')
        
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password endpoint.
    """
    email = serializers.EmailField(required=True)

class UserProfileSearchSerializer(HaystackSerializerMixin, UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        search_fields = ("text", "userprofile_id", "first_name", "last_name", "username", "skills_text", 'created_on')
        field_aliases = {}
        exclude = {}

# class UserProfileSearchSerializer(HaystackSerializer):
#     class Meta:
#         index_classes = [UserProfileIndex]
#         fields = ("text", "userprofile_id", "first_name", "last_name", "username", "skills_text", 'created_on', 'term', 'featured')
#         field_aliases = {}
#         exclude = {}

class ProfessionSearchSerializer(HaystackSerializer):

    class Meta:
        index_classes = [ProfessionIndex]
        fields = ["profession_id", "text", "autocomplete"]
        ignore_fields = ["autocomplete"]

        field_aliases = {
            'q': 'autocomplete'
        }

class SkillSearchSerializer(HaystackSerializer):

    class Meta:
        index_classes = [SkillIndex]
        fields = ["skill_id", "text", "autocomplete"]
        ignore_fields = ["autocomplete"]

        field_aliases = {
            'q': 'autocomplete'
        }
