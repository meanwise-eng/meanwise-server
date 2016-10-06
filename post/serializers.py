from rest_framework import serializers

from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer

from post.models import Post, Comment, Share

class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    class Meta:
        model = Post

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment

class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share



