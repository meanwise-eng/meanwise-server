from django.db.models import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from common.utils import camel_case_to_snake_case
from subscribe.models import Invite
from geography.models import City
from geography.serializers import CitySerializer, UpdateProfileCitySerializer
from interests.serializers import ProfileInterestSerializer, UpdateProfileInterestSerializer

from .models import Profile, LookingFor, Skill, Profession, Language
from .fields import UsernameField
from .constants import OnboardingStage


class UpdateLookingForSerializer(serializers.Serializer):
    id  = serializers.IntegerField(required=True, read_only=False)

class LookingForSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookingFor
        fields = ('id', 'code', 'text',)

class SkillSerializer(serializers.Serializer):
    id      = serializers.IntegerField(required=False, read_only=False)
    text    = serializers.CharField(required=False, read_only=False)

class LanguageSerializer(serializers.Serializer):
    id      = serializers.IntegerField(required=False, read_only=False)
    text    = serializers.CharField(required=False, read_only=False)

class ProfessionSerializer(serializers.Serializer):
    id      = serializers.IntegerField(required=False, read_only=False)
    text    = serializers.CharField(required=False, read_only=False)

class ValidateUsernameSerializer(serializers.Serializer):
    '''
    This class is used for validating a username.
    It checks for regex and uniqueness of Username for now.
    '''
    username    = UsernameField([Profile, Invite], max_length=25, min_length=3)

class RelatedProfileSerializer(serializers.ModelSerializer):
    '''
    Every profile is related with other profiles. It could be via likes,
    or could be followers or following. Each one of those is represented
    via this serializer.
    '''
    username    = serializers.CharField()
    firstName   = serializers.CharField(source='first_name')
    middleName  = serializers.CharField(source='middle_name')
    lastName    = serializers.CharField(source='last_name')
    photo       = serializers.CharField(source='profile_photo_url')

    class Meta:
        model = Profile
        fields = ('id', 'username', 'firstName', 'middleName', 'lastName', 'photo',)


class NotificationProfileSerializer(serializers.ModelSerializer):
    text        = serializers.CharField(source='full_name')
    slug        = serializers.CharField(source='username')
    type        = serializers.SerializerMethodField()
    photo       = serializers.CharField(source='profile_photo_url')

    class Meta:
        model   = Profile
        fields  = ('id', 'text', 'slug', 'type', 'photo',)

    def get_type(self, obj):
        return 'profile'

class PublicProfileDetailSerializer(serializers.ModelSerializer):
    firstName       = serializers.CharField(source='first_name')
    middleName      = serializers.CharField(source='middle_name')
    lastName        = serializers.CharField(source='last_name')
    lookingFor      = LookingForSerializer(source='looking_for')
    onboardingStage = serializers.CharField(source='onboarding_stage')
    interests       = ProfileInterestSerializer(many=True)
    skills          = SkillSerializer(many=True)
    languages       = LanguageSerializer(many=True)
    profilePhoto    = serializers.CharField(source='profile_photo_url')
    coverPhoto      = serializers.CharField(source='cover_photo_url')
    profession      = ProfessionSerializer()
    profileViews    = serializers.IntegerField(source='profile_views')
    followerCount   = serializers.IntegerField(source='follower_count')
    followingCount  = serializers.IntegerField(source='following_count')
    likeCount       = serializers.IntegerField(source='like_count')
    city            = CitySerializer()
    followingIds    = serializers.ListField(child=serializers.IntegerField(), source='following_ids')
    followerIds     = serializers.ListField(child=serializers.IntegerField(), source='follower_ids')
    likedIds        = serializers.ListField(child=serializers.IntegerField(), source='liked_ids')
    likedByIds      = serializers.ListField(child=serializers.IntegerField(), source='liked_by_ids')

    class Meta:
        model = Profile
        fields = ('id', 'username', 'firstName', 'middleName', 'lastName', 'message',
                'description', 'onboardingStage', 'lookingFor', 'skills', 'interests',
                'profilePhoto', 'coverPhoto', 'profession', 'profileViews', 'languages',
                'followerCount', 'likeCount', 'followingCount', 'city', 'followingIds',
                'followerIds', 'likedIds', 'likedByIds', 'links')
        depth = 2

class SimilarProfileDetailSerializer(PublicProfileDetailSerializer):
    class Meta(PublicProfileDetailSerializer.Meta):
        pass

class DefaultProfileDetailSerializer(PublicProfileDetailSerializer):
    pass

class OwnProfileDetailSerializer(PublicProfileDetailSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'email', 'username', 'firstName', 'middleName', 'lastName',
                'message', 'description', 'onboardingStage', 'lookingFor', 'skills',
                'interests', 'profilePhoto', 'coverPhoto', 'profession', 'languages',
                'profileViews', 'followerCount', 'likeCount', 'followingCount',
                'city', 'followingIds', 'followerIds', 'likedIds', 'likedByIds', 'links',)
        depth = 2

class UpdateProfileDetailSerializer(serializers.ModelSerializer):
    username        = UsernameField([Profile, Invite], max_length=25, min_length=3, required=False)
    firstName       = serializers.CharField(max_length=128, required=False)
    middleName      = serializers.CharField(max_length=128, required=False, allow_blank=True)
    lastName        = serializers.CharField(max_length=128, required=False)
    message         = serializers.CharField(max_length=140, required=False, allow_blank=True)
    description     = serializers.CharField(max_length=1024, required=False, allow_blank=True)
    onboardingStage = serializers.ChoiceField(OnboardingStage.choices(), required=False)
    interests       = UpdateProfileInterestSerializer(many=True, required=False)
    skills          = SkillSerializer(many=True, required=False)
    lookingFor      = UpdateLookingForSerializer(required=False)
    profession      = ProfessionSerializer(required=False)
    city            = UpdateProfileCitySerializer(required=False)
    languages       = LanguageSerializer(many=True, required=False)

    class Meta:
        model = Profile
        fields = ('username', 'firstName', 'middleName', 'lastName', 'message',
                'description', 'onboardingStage', 'interests', 'skills', 'lookingFor',
                'profession', 'city', 'languages', 'links',)

    def update(self, instance):
        from django.db import transaction
        with transaction.atomic():
            try:
                interests   = self.validated_data.pop('interests')
            except KeyError as e:
                interests_present = False
            else:
                interests_present = True
                interest_ids = [i['id'] for i in interests if i.get('id')]
                instance.interests = interest_ids

            try:
                skills_data = self.validated_data.pop('skills')
            except KeyError as e:
                skills_present = False
            else:
                skills_present = True
                skills = []
                for skill_data in skills_data:
                    skill = Skill.objects.create_or_get_from_data(skill_data)
                    if skill: skills.append(skill)
                instance.skills = skills

            try:
                languages_data = self.validated_data.pop('languages')
            except KeyError as e:
                languages_present = False
            else:
                languages_present = True
                languages = []
                for language_data in languages_data:
                    language = Language.objects.create_or_get_from_data(language_data)
                    if language: languages.append(language)
                instance.languages = languages

            try:
                profession_data = self.validated_data.pop('profession')
            except KeyError as e:
                profession_present = False
            else:
                profession = Profession.objects.create_or_get_from_data(profession_data)
                instance.profession = profession
                profession_present = True

            try:
                looking_for = self.validated_data.pop('lookingFor')
            except KeyError as e:
                looking_for_present = False
            else:
                try:
                    looking_for = LookingFor.objects.get(id=looking_for['id'], published=True)
                except ObjectDoesNotExist as e:
                    looking_for_present = False
                else:
                    looking_for_present = True
                    instance.looking_for = looking_for

            try:
                city_data = self.validated_data.pop('city')
            except KeyError as e:
                city_present = False
            else:
                try:
                    city = City.objects.get(id=city_data['id'])
                except ObjectDoesNotExist as e:
                    city_present = False
                else:
                    instance.city = city
                    city_present = True

            for key, value in self.validated_data.items():
                setattr(instance, camel_case_to_snake_case(key), value)
            instance.save()

            if skills_present:
                self.validated_data['skills'] = SkillSerializer(instance.skills, many=True).data
            if interests_present:
                self.validated_data['interests'] = ProfileInterestSerializer(instance.interests, many=True).data
            if looking_for_present:
                self.validated_data['lookingFor'] = LookingForSerializer(instance.looking_for).data
            if profession_present:
                self.validated_data['profession'] = ProfessionSerializer(instance.profession).data
            if city_present:
                self.validated_data['city'] = CitySerializer(instance.city).data
            if languages_present:
                self.validated_data['languages'] = LanguageSerializer(instance.languages, many=True).data
        return instance
