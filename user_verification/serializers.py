from rest_framework import serializers

from .models import UserVerification


class UserVerificationSerializer(serializers.ModelSerializer):

    class Meta():
        model = UserVerification
        fields = ('id', 'probability', 'match', 'match_id',)


class VerifyUserSerializer(serializers.Serializer):
    
    profile_id = serializers.UUIDField()
    media_file = serializers.CharField(max_length=255)
