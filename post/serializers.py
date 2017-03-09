from rest_framework import serializers

from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from easy_thumbnails.files import get_thumbnailer

from userprofile.models import UserProfile
from post.models import Post, Comment, Share

from drf_haystack.serializers import HaystackSerializerMixin

class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    #tags = TagListSerializerField()
    user_id = serializers.SerializerMethodField()
    num_likes = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()
    interest_id = serializers.SerializerMethodField()
    user_firstname = serializers.SerializerMethodField()
    user_lastname = serializers.SerializerMethodField()
    user_profile_photo = serializers.SerializerMethodField()
    user_cover_photo = serializers.SerializerMethodField()
    user_profession = serializers.SerializerMethodField()
    user_profile_photo_small = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    video_thumb_url = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id', 'text', 'user_id', 'num_likes', 'num_comments', 'interest_id', 'user_firstname', 'user_lastname',
                      'user_profile_photo', 'user_cover_photo', 'user_profile_photo_small', 'user_profession',
                      'image_url', 'video_url', 'video_thumb_url', 'resolution', 'liked_by', 'created_on')

    def get_user_id(self, obj):
        user_id = obj.poster.id
        return user_id

    def get_interest_id(self, obj):
        return obj.interest.id

    def get_user_firstname(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return  ""
        return up.first_name

    def get_user_lastname(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return  ""
        return up.last_name

    def get_user_profile_photo(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return  ""
        if up.profile_photo:
            return up.profile_photo.url
        return ""

    def get_user_cover_photo(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return  ""
        if up.cover_photo:
            return up.cover_photo.url
        return ""
    
    def get_user_profile_photo_small(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return  ""
        small = {'size': (48, 48), 'crop': True}
        profile_photo_small_url = ""
        if up.profile_photo:
            profile_photo_small_url = get_thumbnailer(up.profile_photo).get_thumbnail(small).url
            return profile_photo_small_url
        return ""

    def get_user_profession(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return  ""
        profession = up.profession
        data = {}
        if profession:
            data = {
                'name': profession.text,
                'id': profession.id,
                }
        return data

    def get_num_likes(self, obj):
        return obj.liked_by.all().count()

    def get_num_comments(self, obj):
        return Comment.objects.filter(post=obj).count()

    def get_liked_by(self, obj):
        liked_by = []
        for user in obj.liked_by.all():
            liked_by.append(user.id)

        return liked_by

    def get_image_url(self, obj):
        _image = obj.image
        if _image:
            return _image.url
        return ""

    def get_video_url(self, obj):
        _video = obj.video
        if _video:
            return _video.url
        return ""

    def get_video_thumb_url(self, obj):
        #needs to be added
        if obj.video:
            if obj.video_thumbnail:
                return obj.video_thumbnail.url
        else:
            return ""

    def get_resolution(self, obj):
        if obj.image:
            return {'height':obj.image.height, 'width':obj.image.width}
        elif obj.video:
            #needs to be done
            
            #return {'height':obj.video_height, 'width':obj.video_width}
            return {'height':320, 'width':240}

class PostSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post

class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    user_first_name = serializers.SerializerMethodField()
    user_last_name = serializers.SerializerMethodField()
    user_profile_photo = serializers.SerializerMethodField()
    user_profile_photo_small = serializers.SerializerMethodField()
    
    
    post_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'comment_text', 'user_id', 'user_username', 'user_first_name', 'user_last_name',
                      'user_profile_photo', 'user_profile_photo_small',
                      'post_id', 'created_on')

    def get_user_id(self, obj):
        user_id = obj.commented_by.id
        return user_id

    def get_user_username(self, obj):
        try:
            user_up = obj.commented_by.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if user_up:
            return user_up.username
        return ""

    def get_user_first_name(self, obj):
        try:
            user_up = obj.commented_by.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if user_up:
            return user_up.first_name
        return ""

    def get_user_last_name(self, obj):
        try:
            user_up = obj.commented_by.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if user_up:
            return user_up.last_name
        return ""

    def get_post_id(self, obj):
        post_id = obj.post.id
        return post_id

    def get_user_profile_photo(self, obj):
        try:
            up = obj.commented_by.userprofile
        except UserProfile.DoesNotExist:
            return  ""
        if up.profile_photo:
            return up.profile_photo.url
        return  ""

    def get_user_profile_photo_small(self, obj):
        try:
            up = obj.commented_by.userprofile
        except UserProfile.DoesNotExist:
            return  ""
        small = {'size': (48, 48), 'crop': True}
        profile_photo_small_url = ""
        if up.profile_photo:
            profile_photo_small_url = get_thumbnailer(up.profile_photo).get_thumbnail(small).url
            return profile_photo_small_url
        return  ""

        
class CommentSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment

class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share

class PostSearchSerializer(HaystackSerializerMixin, PostSerializer):
    class Meta(PostSerializer.Meta):
        search_fields = ("text", "interest_name", "post_text", "created_on", "post_id")


        
