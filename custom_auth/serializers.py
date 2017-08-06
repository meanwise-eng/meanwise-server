from django.http import HttpRequest
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core import exceptions
import logging

import ast

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from requests.exceptions import HTTPError
import django.contrib.auth.password_validation as validators

from django.contrib.auth.models import User
from userprofile.models import *
from userprofile.serializers import UserProfileSerializer

logger = logging.getLogger('meanwise_backend.%s' % __name__)


class RegisterUserSerializer(serializers.Serializer):
    """
    Handle user registration.

    """
    username = serializers.CharField(max_length=200)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(max_length=200, required=False)
    facebook_token = serializers.CharField(max_length=128, required=False)
    first_name = serializers.CharField(max_length=128)
    middle_name = serializers.CharField(required=False)
    last_name = serializers.CharField(max_length=128, required=False)
    profession = serializers.IntegerField(source='Profession', required=False)
    city = serializers.CharField(max_length=128, required=False)
    skills = serializers.ListField()
    interests = serializers.ListField()
    profile_photo = serializers.ImageField(required=False)
    cover_photo = serializers.ImageField(required=False)
    bio = serializers.CharField(max_length=200, required=False)
    profile_story_title = serializers.CharField(max_length=128, required=False)
    profile_story_description = serializers.CharField(max_length=200, required=False)
    dob = serializers.DateField(required=False)

    skills_list = serializers.ListField()
    profession_text = serializers.CharField(max_length=123, required=False)

    profile_background_color = serializers.CharField(max_length=20)

    def validate_username(self, value):
        """
        Check that the username does not exist already.
        """
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            return value
        raise serializers.ValidationError("User with username already exists.")

    def validate_email(self, value):
        """
        Check that the email does not exist already.
        """
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            return value
        raise serializers.ValidationError("User with email already exists.")

    def save(self):
        # check
        username = self.validated_data['username']
        email = self.validated_data['email']
        password = self.validated_data.get('password', None)
        if password:
            errors = dict()
            try:
                validators.validate_password(password=password, user=User)
            except exceptions.ValidationError as e:
                errors['password'] = list(e.messages)
            if errors:
                raise serializers.ValidationError(errors)
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
        elif self.validated_data.get('facebook_token', None):
            user = User.objects.create(username=username,
                                       email=email)
            user.set_password('P@ssw0rd123!')
            user.save()
        token = Token.objects.get_or_create(user=user)
        user_profile = UserProfile()
        user_profile.user = user
        print ("validated_data", self.validated_data)
        user_profile.first_name = self.validated_data['first_name']
        if self.validated_data.get('middle_name', None):
            user_profile.middle_name = self.validated_data['middle_name']
        if self.validated_data.get('last_name', None):
            user_profile.last_name = self.validated_data['last_name']
        if self.validated_data.get('city', None):
            user_profile.city = self.validated_data['city']
        if self.validated_data.get('profile_photo', None):
            user_profile.profile_photo = self.validated_data['profile_photo']
        if self.validated_data.get('cover_photo', None):
            user_profile.cover_photo = self.validated_data['cover_photo']
        if self.validated_data.get('bio', None):
            user_profile.bio = self.validated_data['bio']
        if self.validated_data.get('profile_story_title', None):
            user_profile.profile_story_title = self.validated_data['profile_story_title']
        if self.validated_data.get('profile_story_description', None):
            user_profile.profile_story_description = self.validated_data[
                'profile_story_description']
        if self.validated_data.get('dob', None):
            user_profile.dob = self.validated_data['dob']
        if self.validated_data.get('facebook_token', None):
            user_profile.facebook_token = self.validated_data['facebook_token']
        if self.validated_data.get('profile_background_color', None):
            user_profile.profile_background_color = self.validated_data['profile_background_color']

        try:
            user_profile.save()
        except Exception as ex:
            logger.error(ex)
            raise

        if self.validated_data.get('profession', None):
            try:
                profession = Profession.objects.get(id=int(self.validated_data['profession']))
                user_profile.profession = profession
                user_profile.save()
            except Profession.DoesNotExist:
                logger.warning("Error adding profession to profile during registration",
                               self.validated_data['profession'])
        if self.validated_data.get('profession_text', None):
            try:
                user_profile.profession_text = self.validated_data['profession_text']
                profession = Profession.objects.get(text=self.validated_data['profession_text'])
                user_profile.profession = profession
                user_profile.save()
            except Profession.DoesNotExist:
                pass
        skills_list_from_skills = list()
        if self.validated_data.get('skills', None):
            # hack to handle llist as string
            skills = self.validated_data.get('skills')
            logger.info("Skills: %s of type %s" % (skills, type(skills)))
            if type(skills) == str or type(skills) == int:
                skills = list(skills)
            if type(skills[0]) == str and skills[0].find('(') != -1:
                skills = ast.literal_eval(skills[0])
            for skill in skills:
                try:
                    skill = Skill.objects.get(id=int(skill))
                    user_profile.skills.add(skill)
                except Skill.DoesNotExist:
                    logger.warning("Error adding skill to profile during registration", skill)

            skills_list_from_skills = [skill.text for skill in user_profile.skills.all()]

        if self.validated_data.get('skills_list', None):
            skills_list = self.validated_data.get('skills_list', list())
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
                    user_profile.skills.add(skill)
                except Skill.DoesNotExist:
                    pass
            user_profile.skills_list = list(set(skills_list + skills_list_from_skills))
            #user_profile.skills_list = list(skills_list)
            user_profile.save()

        if self.validated_data.get('interests', None):
            # hack to handle llist as string
            interest_ids = self.validated_data.get('interests')
            if type(interest_ids) == str or type(interest_ids) == int:
                interest_ids = list(interest_ids)
            if type(interest_ids[0]) == str and interest_ids[0].find('[') != -1:
                interest_ids = ast.literal_eval(interest_ids[0])
            for interest_id in interest_ids:
                try:
                    interest = Interest.objects.get(id=int(interest_id))
                    user_profile.interests.add(interest)
                except Profession.DoesNotExist:
                    logger.warning(
                        "Error adding interest to profile during registration", interest)

        # add to invite group count
        #invite_group = InviteGroup.objects.get(invite_code=self.validated_data['invite_code'])
        #invite_group.count += 1
        # invite_group.save()
        # invite_group.users.add(user)
        return user, user_profile, token[0].key


class RegisterFacebookUserSerializer(RegisterUserSerializer):
    """
    Handle facebook user registration.

    """
    facebook_token = serializers.CharField(max_length=128)

    def save(self):
        username = self.validated_data['username']
        email = self.validated_data['email']
        password = self.validated_data['password']
        user = User.objects.create(username=username,
                                   password=password, email=email)
        token = Token.objects.get_or_create(user=user)
        user_profile = UserProfile()
        user_profile.first_name = self.validated_data['first_name']
        if self.validated_data.get('middle_name', None):
            user_profile.middle_name = self.validated_data['middle_name']
        if self.validated_data.get('last_name', None):
            user_profile.last_name = self.validated_data['last_name']
        if self.validated_data.get('city', None):
            user_profile.city = self.validated_data['city']
        if self.validated_data.get('profile_photo', None):
            user_profile.profile_photo = self.validated_data['profile_photo']
        if self.validated_data.get('cover_photo', None):
            user_profile.cover_photo = self.validated_data['cover_photo']
        if self.validated_data.get('bio', None):
            user_profile.bio = self.validated_data['bio']
        user_profile.save()
        if self.validated_data.get('profession', None):
            try:
                profession = Profession.objects.get(id=int(self.validated_data['profession']))
                user_profile.profession = profession
                user_profile.save()
            except Profession.DoesNotExist:
                logger.warning("Error adding profession to profile during registration",
                               self.validated_data['profession'])
        if self.validated_data.get('skills', None):
            for skill in self.validated_data['skills']:
                try:
                    skill = Skill.objects.get(id=int(skill))
                    user_profile.skills.add(skill)
                except Profession.DoesNotExist:
                    logger.warning("Error adding skill to profile during registration", skill)
        if self.validated_data.get('interests', None):
            for interest in self.validated_data['interests']:
                try:
                    interest = Interest.objects.get(id=int(interest))
                    user_profile.interests.add(interest)
                except Profession.DoesNotExist:
                    logger.warning(
                        "Error adding interest to profile during registration", interest)
        return user, user_profile, token[0].key
