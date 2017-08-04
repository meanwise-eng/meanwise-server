from django.db import models

import os

from django.db import models
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.postgres.fields.jsonb import JSONField as pgJSONField

from post.models import Post, Comment
from userprofile.models import UserFriend

from scarface.models import Device

NOTIFICATION_TYPES = (
    ('FA', 'FriendRequestAccepted'),
    ('FR', 'FriendRequestReceived'),
    ('LP',  'LikedPost'),
    ('CP', 'CommentedPost'),
    ('UK', 'Unknown'),
    )


class Notification(models.Model):
    TYPE_FRIEND_REQUEST_ACCEPTED = 'FA'
    TYPE_FRIEND_REQUEST_REJECTED = 'FR'
    TYPE_LIKED_POST = 'LP'
    TYPE_COMMENTED_POST = 'CP'
    TYPE_UNKNOWN = 'UK'

    receiver = models.ForeignKey(User, related_name='receiver')
    notification_type = models.CharField(max_length=2, default="UK", choices=NOTIFICATION_TYPES)
    user_friend = models.ForeignKey(UserFriend, blank=True, null=True)
    post = models.ForeignKey(Post, blank=True, null=True)
    comment = models.ForeignKey(Comment, blank=True, null=True)
    post_liked_by = models.ForeignKey(User, related_name='post_liked_by', blank=True, null=True)
    data = pgJSONField(null=True)
    was_notified = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Notification id: " + str(self.id)  + " for: " + str(self.receiver) + " type: " + str(self.notification_type)

class ASNSDevice(models.Model):
    user = models.ForeignKey(User)
    device = models.ForeignKey(Device)

    def __str__(self):
        return "ASNS Device id: " + str(self.id)  + " user: " + str(self.user) + " device: " + str(self.device.device_id)
