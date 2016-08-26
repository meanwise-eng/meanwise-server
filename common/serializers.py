from rest_framework import serializers

from account_profile.serializers import RelatedProfileSerializer

from .models import Comment
from .fields import TimestampField


class CommentSerializer(serializers.ModelSerializer):
    profile = RelatedProfileSerializer(read_only=True)
    createdOn = TimestampField(source='created_on', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'createdOn', 'profile', 'createdOn',)

    def create(self, validated_data, profile, instance):
        comment = Comment()
        comment.instance = instance
        comment.profile = profile
        comment.text = validated_data['text']
        comment.save()
        return comment

    def update(self, validated_data, instance):
        instance.text = validated_data['text']
        instance.save()
        return instance
