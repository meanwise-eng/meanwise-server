from django.http import HttpRequest
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core import exceptions

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from requests.exceptions import HTTPError
import django.contrib.auth.password_validation as validators

from django.contrib.auth.models import User
from userprofile.models import *
from userprofile.serializers import UserProfileSerializer


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
    profession = serializers.IntegerField(source='Profession')
    city = serializers.CharField(max_length=128, required=False)
    skills = serializers.ListField()
    interests = serializers.ListField()
    profile_photo = serializers.ImageField(required=False)
    cover_photo = serializers.ImageField(required=False)
    bio = serializers.CharField(max_length=200, required=False)
    invite_code = serializers.CharField(max_length=128, required=True)

    def validate_invite_code(self, value):
        """
        Check that the invite code is valid.
        """
        try:
            invite_group = InviteGroup.objects.get(invite_code=value)
        except InviteGroup.DoesNotExist:
            raise serializers.ValidationError("Not a valid invite code.")
        return value

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
        #check
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
            user = User.objects.create(username=username,
                                       password=password, email=email)
        elif self.validated_data.get('facebook_token', None):
            user = User.objects.create(username=username,
                                       password='password', email=email)
        token = Token.objects.get_or_create(user=user)
        user_profile = UserProfile()
        user_profile.user = user
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
        if self.validated_data.get('facebook_token', None):
            user_profile.facebook_token = self.validated_data['facebook_token']
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
                    logger.warning("Error adding interest to profile during registration", interest)

        #add to invite group count
        invite_group = InviteGroup.objects.get(invite_code=self.validated_data['invite_code'])
        invite_group.count += 1
        invite_group.save()
        invite_group.users.add(user)
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
                logger.warning("Error adding profession to profile during registration", self.validated_data['profession'])
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
                    logger.warning("Error adding interest to profile during registration", interest)
        return user, user_profile, token[0].key
