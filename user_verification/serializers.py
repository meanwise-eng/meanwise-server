from rest_framework import serializers

from .models import UserVerification


class UserVerificationSerializer(serializers.ModelSerializer):

    class Meta():
        model = UserVerification
        fields = ('id', 'probability', 'match', 'match_id',)


class VerifyUserSerializer(serializers.Serializer):
    
    profile_id = serializers.UUIDField()
    media_file = serializers.CharField(max_length=255)


class AudioCheckAndVideoSerializer(serializers.Serializer):

    audio_captcha_sentence = serializers.CharField(max_length=250)
    audio_captcha_result = serializers.BooleanField()
    full_video = serializers.CharField(max_length=255)


class FindFaceSerializer(serializers.Serializer):

    media_file = serializers.CharField(max_length=255)


class FaceSerializer(serializers.Serializer):

    probability = serializers.IntegerField()
    profile_uuid = serializers.UUIDField()
    profile_photo_thumbnail_url = serializers.CharField()

    def get_probability(self, obj):
        return obj['probability']

    def get_profile_uuid(self, obj):
        userprofile = self._get_userprofile(obj['ExternalId'])

        return userprofile.profile_uuid

    def get_profile_photo_thumbnail_url(self, obj):
        userprofile = self._get_userprofile(obj['ExternalId'])

        return userprofile.profile_photo_thumbnail.url

    def _get_userprofile(self, profile_uuid):
        try:
            return UserProfile.objects.get(profile_uuid=profile_uuid)
        except UserProfile.DoesNotExist:
            raise Exception("Cannot find userprofile (%s)" % profile_uuid)
