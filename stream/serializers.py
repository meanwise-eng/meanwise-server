from rest_framework import serializers

from common.fields import TimestampField

from .models import Activity


class ActorSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {'type': 'profile',
                'text': instance.__unicode__(),
                'slug': instance.username
                }


class ActionObjectSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {'type': 'profile',
                'text': instance.__unicode__(),
                'slug': instance.username
                }


class TargetSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {'type': 'profile',
                'text': instance.__unicode__(),
                'slug': instance.username
                }


class NotificationSerializer(serializers.ModelSerializer):
    actor = ActorSerializer()
    verb = serializers.CharField(source='get_verb_display')
    actionObject = ActionObjectSerializer(source='action_object')
    target = TargetSerializer()
    createdOn = TimestampField(source='created_on')

    class Meta:
        model = Activity
        fields = ('actor', 'verb', 'actionObject', 'target', 'createdOn',)
