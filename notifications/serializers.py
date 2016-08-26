from rest_framework import serializers

from common.fields import TimestampField
from account_profile.models import Profile
from works.models import Work
from account_profile.serializers import NotificationProfileSerializer
from works.serializers import NotificationWorkSerializer
from stream.serializers import ActorSerializer, ActionObjectSerializer, TargetSerializer

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor = ActorSerializer()
    type = serializers.CharField(source='get_type_display')
    actionObject = ActionObjectSerializer(source='action_object')
    target = TargetSerializer(source='profile')
    read = serializers.BooleanField()
    createdOn = TimestampField(source='created_on')

    class Meta:
        model = Notification
        fields = ('id', 'actor', 'type', 'actionObject',
                  'target', 'createdOn', 'read',)


class NotificationRedisSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    type = serializers.CharField(source='get_type_display')
    actionObject = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    read = serializers.BooleanField()
    createdOn = TimestampField(source='created_on')

    class Meta:
        model = Notification
        fields = ('id', 'actor', 'type', 'actionObject',
                  'target', 'createdOn', 'read',)

    def get_actor(self, obj):
        return Profile.cache.get_cache_key(obj.actor,
                                           NotificationProfileSerializer)

    def get_actionObject(self, obj):
        if obj.action_object:
            return Profile.cache.get_cache_key(obj.action_object,
                                               NotificationProfileSerializer)
        else:
            return ''

    def get_target(self, obj):
        if type(obj.target) == Profile:
            return Profile.cache.get_cache_key(obj.target,
                                               NotificationProfileSerializer)
        elif type(obj.target) == Work:
            return Work.cache.get_cache_key(obj.target,
                                            NotificationWorkSerializer)
        else:
            raise Exception('Invalid target type in notification')
