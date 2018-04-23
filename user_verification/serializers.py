from rest_framework import serializers

from .models import UserVerification
from userprofile.models import UserProfile


class UserVerificationSerializer(serializers.ModelSerializer):

    class Meta():
        model = UserVerification
        fields = ('id', 'probability', 'match', 'match_id',)


class VerifyUserSerializer(serializers.Serializer):
    
    profile_uuid = serializers.UUIDField()
    media_file = serializers.CharField(max_length=255)


class AudioCheckAndVideoSerializer(serializers.Serializer):

    audio_captcha_sentence = serializers.CharField(max_length=250)
    audio_captcha_result = serializers.BooleanField()
    full_video = serializers.CharField(max_length=255)


class FindFaceSerializer(serializers.Serializer):

    media_file = serializers.CharField(max_length=255)


class FaceSerializer(serializers.Serializer):

    probability = serializers.SerializerMethodField()
    profile_uuid = serializers.SerializerMethodField()
    profile_photo_thumbnail_url = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    profession = serializers.SerializerMethodField()

    def get_probability(self, obj):
        return obj['Face']['Confidence']

    def get_profile_uuid(self, obj):
        userprofile = self._get_userprofile(obj)

        return userprofile.profile_uuid

    def get_profile_photo_thumbnail_url(self, obj):
        userprofile = self._get_userprofile(obj)

        return userprofile.profile_photo_thumbnail.url

    def get_fullname(self, obj):
        userprofile = self._get_userprofile(obj)

        return userprofile.fullname()

    def get_profession(self, obj):
        userprofile = self._get_userprofile(obj)

        return userprofile.profession_text

    def _get_userprofile(self, obj):
        try:
            return UserProfile.objects.get(profile_uuid=obj['Face']['ExternalImageId'])
        except UserProfile.DoesNotExist:
            raise Exception("Cannot find userprofile (%s)" % profile_uuid)
