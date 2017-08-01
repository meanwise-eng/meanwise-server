import datetime

from rest_framework import serializers

from mnotifications.models import Notification
from userprofile.models import UserProfile, UserFriend
from post.models import Post, Comment

from userprofile.serializers import UserSerializer, UserFriendSerializer
from post.serializers import NotificationPostSerializer, CommentSerializer


class NotificationSerializer(serializers.ModelSerializer):
    receiver = UserSerializer(read_only=True)
    post_liked_by = UserSerializer(read_only=True)
    post_mentioned_users = UserSerializer(read_only=True)
    c_mentioned_users = UserSerializer(read_only=True)
    post = NotificationPostSerializer(read_only=True)
    comment = CommentSerializer(read_only=True)
    notification_type = serializers.SerializerMethodField()
    user_friend = UserFriendSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'receiver', 'notification_type', 'user_friend',
                  'post', 'comment', 'post_liked_by', 'post_mentioned_users',
                  'c_mentioned_users', 'was_notified', 'created_on')

    def get_notification_type(self, obj):
        return obj.get_notification_type_display()
