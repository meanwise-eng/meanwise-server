from rest_framework import serializers

from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from easy_thumbnails.files import get_thumbnailer

from userprofile.models import UserProfile
from post.models import Post, Comment, Share, Story
from post.search_indexes import PostIndex

from drf_haystack.serializers import HaystackSerializer, HaystackSerializerMixin

class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    num_likes = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()
    interest_id = serializers.SerializerMethodField()
    user_firstname = serializers.SerializerMethodField()
    user_lastname = serializers.SerializerMethodField()
    user_profile_photo = serializers.SerializerMethodField()
    user_cover_photo = serializers.SerializerMethodField()
    user_profession = serializers.SerializerMethodField()
    user_profession_text = serializers.SerializerMethodField()
    user_profile_photo_small = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    video_thumb_url = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()
    story = serializers.HyperlinkedRelatedField(
        read_only=True,
        allow_null=True,
        lookup_url_kwarg='story_id',
        view_name='post-story'
    )
    queryset=Post.objects.filter(is_deleted=False)
    
    class Meta:
        model = Post
        fields = ('id', 'text', 'user_id', 'num_likes', 'num_comments', 'interest_id', 'user_firstname', 'user_lastname',
                      'user_profile_photo', 'user_cover_photo', 'user_profile_photo_small', 'user_profession', 'user_profession_text',
                      'image_url', 'video_url', 'video_thumb_url', 'resolution', 'liked_by', 'created_on', 'tags', 'topics',
                      'story', 'story_index')

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
        if up.profile_photo_thumbnail:
            return up.profile_photo_thumbnail.url
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

    def get_user_profession_text(self, obj):
        try:
            up = obj.poster.userprofile
            return up.profession_text
        except UserProfile.DoesNotExist:
            return  None

    def get_num_likes(self, obj):
        return obj.liked_by.all().count()

    def get_topics(self, obj):
        return obj.topics.all().values_list('text',flat=True)

    def get_tags(self, obj):
        return obj.tags.all().values_list('name',flat=True)

    def get_num_comments(self, obj):
        return Comment.objects.filter(post=obj).filter(is_deleted=False).count()

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

class NotificationPostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
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
    topics = serializers.SerializerMethodField()
    queryset=Post.objects.filter(is_deleted=False)
    
    class Meta:
        model = Post
        fields = ('id', 'text', 'user_id', 'num_likes', 'num_comments', 'interest_id', 'user_firstname', 'user_lastname',
                      'user_profile_photo', 'user_cover_photo', 'user_profile_photo_small', 'user_profession',
                      'image_url', 'video_url', 'video_thumb_url', 'resolution', 'liked_by', 'created_on', 'tags', 'topics',
                      'story_index')

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
        if up.profile_photo_thumbnail:
            return up.profile_photo_thumbnail.url
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

    def get_topics(self, obj):
        return obj.topics.all().values_list('text',flat=True)

    def get_tags(self, obj):
        return obj.tags.all().values_list('name',flat=True)

    def get_num_comments(self, obj):
        return Comment.objects.filter(post=obj).filter(is_deleted=False).count()

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
    tags = TagListSerializerField(required=False)
    topics = serializers.SerializerMethodField()
    topic_names = serializers.CharField(required=False, max_length=100, allow_blank=True)
    class Meta:
        model = Post

    def get_topics(self, obj):
        return obj.topics.all().values_list('text',flat=True)

class StorySerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()
    class Meta:
        model = Story
        fields = ('id', 'main_post', 'posts')

    def get_posts(self, obj):
        return PostSerializer(obj.posts.filter(is_deleted=False), many=True, context=self.context).data

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
        search_fields = ("text", "interest_name", "post_text", "created_on", "post_id", "topic_texts", "tag_names")
        field_aliases = {}
        exclude = tuple()


        
