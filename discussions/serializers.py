
from rest_framework import serializers
from .models import DiscussionItem


class DiscussionItemSerializer(serializers.ModelSerializer):

    post_id = serializers.SerializerMethodField()
    comment_id = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()
    userprofile = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionItem
        fields = ('text', 'type', 'datetime', 'post_id', 'comment_id', 'userprofile', 'post')

    def get_post_id(self, obj):
        return obj.post.id

    def get_comment_id(self, obj):
        return obj.comment.id

    def get_post(self, obj):
        post = obj.post
        return {
            'id': post.id,
            'image_url': post.image.url if post.image else post.video_thumbnail.url,
            'text': post.text
        }

    def get_userprofile(self, obj):
        u = obj.post.poster.userprofile
        return {
            'id': obj.post.poster.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'username': u.username,
            'user_id': obj.post.poster.id,
            'profile_photo_thumbnail_url': u.profile_photo_thumbnail.url
        }
