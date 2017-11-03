import datetime
import json

from rest_framework import serializers
from django.urls import reverse
from common.api_helper import build_absolute_uri

from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from common.api_helper import build_absolute_uri

from django.contrib.auth.models import User
from userprofile.models import UserProfile, Profession
from post.models import Post, Comment, Share, Story
from post.documents import PostDocument
from brands.models import Brand

from drf_haystack.serializers import HaystackSerializerMixin
from drf_haystack.serializers import HaystackSerializer, HaystackSerializerMixin
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer


class PostDocumentSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()
    num_comments = serializers.IntegerField()
    interest_id = serializers.IntegerField()
    user_firstname = serializers.CharField()
    user_lastname = serializers.CharField()
    user_profile_photo = serializers.CharField()
    user_profile_photo_small = serializers.CharField()
    user_cover_photo = serializers.CharField()
    user_profession_text = serializers.CharField()
    text = serializers.CharField()
    image_url = serializers.CharField()
    video_url = serializers.CharField()
    video_thumb_url = serializers.CharField()
    created_on = serializers.DateTimeField()
    resolution = serializers.CharField()
    mentioned_users = serializers.ListField(serializers.DictField())
    brand = serializers.CharField()
    brand_logo_url = serializers.CharField()
    post_type = serializers.CharField()
    panaroma_type = serializers.CharField()
    post_thumbnail_url = serializers.CharField()
    is_work = serializers.BooleanField()
    link = serializers.CharField()
    pdf_url = serializers.CharField()
    audio_url = serializers.CharField()
    pdf_thumb_url = serializers.CharField()
    audio_thumb_url = serializers.CharField()

    id = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()
    user_profession = serializers.SerializerMethodField()
    created_on = serializers.SerializerMethodField()
    likes_url = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()
    mentioned_users = serializers.SerializerMethodField()
    boost_datetime = serializers.SerializerMethodField()
    link_meta_data = serializers.SerializerMethodField()
    user_profession = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj._id

    def get_score(self, obj):
        return obj._score if hasattr(obj.meta, 'score') else None

    def get_user_profession(self, obj):
        if not obj.user_profession_id:
            return None

        profession = Profession.objects.get(id=obj.user_profession_id)

        return {
            'name': profession.text,
            'id': profession.id
        }

    def get_created_on(self, obj):
        return obj.created_on

    def get_is_liked(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            request = self.context.get('request')
            if not request or not hasattr(request, 'user'):
                return False

            if not request.user.id:
                return False

            user_id = request.user.id

        liked_ids = list(User.objects.filter(liked_by=obj._id).all().values_list('id', flat=True))

        if user_id not in liked_ids:
            return False

        return True

    def get_likes_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        return build_absolute_uri(reverse('post-likes', args=[obj._id]))

    def get_resolution(self, obj):
        post = self.get_post(obj)
        return post.resolution

    def get_mentioned_users(self, obj):
        post = Post.objects.get(id=obj._id)

        return [{'id': u.id, 'username': u.username} for u in post.mentioned_users.all()]

    def get_boost_datetime(self, obj):
        return obj.boost_datetime

    def get_link_meta_data(self, obj):
        post = self.get_post(obj)

        return post.link_meta_data

    def get_post(self, obj):
        try:
            post = Post.objects.get(id=obj._id)
        except Post.DoesNotExist:
            raise Exception("Post doesn't exist in db for ID: %s" % obj._id)

        return post

    def get_user_profession(self, doc):
        obj = self.get_post(doc)
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        profession = up.profession
        data = {}
        if profession:
            data = {
                'name': profession.text,
                'id': profession.id,
            }
        return data

    def get_topics(self, obj):
        if obj.topics:
            return list(obj.topics)

        return []

    def get_tags(self, obj):
        if obj.tags:
            return list(obj.tags)

        return []


class MentionedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    num_likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    likes_url = serializers.SerializerMethodField()
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
    topics = serializers.SerializerMethodField()
    mentioned_users = MentionedUserSerializer(many=True, read_only=True)
    pdf_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    pdf_thumb_url = serializers.SerializerMethodField()
    audio_thumb_url = serializers.SerializerMethodField()
    link_meta_data = serializers.SerializerMethodField()
    post_type = serializers.SerializerMethodField()
    brand_logo_url = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    post_thumbnail_url = serializers.SerializerMethodField()

    story = serializers.HyperlinkedRelatedField(
        read_only=True,
        allow_null=True,
        lookup_url_kwarg='story_id',
        view_name='post-story'
    )

    queryset = Post.objects.filter(is_deleted=False)

    class Meta:
        model = Post
        fields = ('id', 'post_type', 'text', 'user_id', 'num_likes', 'num_comments', 'interest_id',
                  'user_firstname', 'user_lastname', 'user_profile_photo', 'user_cover_photo',
                  'user_profile_photo_small', 'user_profession', 'user_profession_text',
                  'image_url', 'video_url', 'video_thumb_url', 'resolution', 'created_on',
                  'tags', 'topics', 'story', 'story_index', 'is_liked', 'likes_url',
                  'mentioned_users', 'geo_location_lat', 'geo_location_lng',
                  'brand', 'brand_logo_url', 'pdf_url', 'link', 'audio_url',
                  'pdf_thumb_url', 'audio_thumb_url', 'link_meta_data', 'panaroma_type',
                  'post_thumbnail_url', 'is_work',
                  )

    def get_user_id(self, obj):
        user_id = obj.poster.id
        return user_id

    def get_interest_id(self, obj):
        return obj.interest.id

    def get_user_firstname(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        return up.first_name

    def get_user_lastname(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        return up.last_name

    def get_user_profile_photo(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.profile_photo:
            return up.profile_photo.url
        return ""

    def get_user_cover_photo(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.cover_photo:
            return up.cover_photo.url
        return ""

    def get_user_profile_photo_small(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.profile_photo_thumbnail:
            return up.profile_photo_thumbnail.url
        return ""

    def get_user_profession(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
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
            return None

    def get_num_likes(self, obj):
        return obj.liked_by.all().count()

    def get_is_liked(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            request = self.context.get('request')
            if not request or not hasattr(request, 'user'):
                return False

            if not request.user.id:
                return False

            user_id = request.user.id

        liked_ids = obj.liked_by.values_list('id', flat=True)

        if user_id not in liked_ids:
            return False

        return True

    def get_likes_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        return build_absolute_uri(reverse('post-likes', args=[obj.id]))

    def get_topics(self, obj):
        return obj.topics.all().values_list('text', flat=True)

    def get_tags(self, obj):
        return obj.tags.all().values_list('name', flat=True)

    def get_num_comments(self, obj):
        return Comment.objects.filter(post=obj).filter(is_deleted=False).count()

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
        # needs to be added
        if obj.video:
            if obj.video_thumbnail:
                return obj.video_thumbnail.url
        else:
            return ""

    def get_pdf_url(self, obj):
        pdf = obj.pdf
        if pdf:
            return pdf.url
        return ""

    def get_pdf_thumb_url(self, obj):
        pdf_thumbnail = obj.pdf_thumbnail
        if pdf_thumbnail:
            return pdf_thumbnail.url
        return ""

    def get_audio_url(self, obj):
        audio = obj.audio
        if audio:
            return audio.url
        return ""

    def get_audio_thumb_url(self, obj):
        audio_thumbnail = obj.audio_thumbnail
        if audio_thumbnail:
            return audio_thumbnail.url
        return ""

    def get_link_meta_data(self, obj):
        return obj.link_meta_data if obj.link_meta_data else None

    def get_post_type(self, obj):
        if obj.image:
            return Post.TYPE_IMAGE
        elif obj.video:
            return Post.TYPE_VIDEO
        elif obj.audio:
            return Post.TYPE_AUDIO
        elif obj.link:
            return Post.TYPE_LINK
        elif obj.pdf:
            return Post.TYPE_PDF
        elif obj.text or not (obj.image and obj.video and obj.link and obj.text and obj.pdf):
            return Post.TYPE_TEXT

    def get_brand_logo_url(self, obj):
        if obj.brand:
            return obj.brand.logo.url

        return None

    def get_brand(self, obj):
        if obj.brand is None:
            return None

        return build_absolute_uri(reverse('brand-details', kwargs={'brand_id': obj.brand.id}))

    def get_post_thumbnail_url(self, obj):
        return obj.post_thumbnail().url if obj.post_thumbnail() else None


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
    user_profession_text = serializers.SerializerMethodField()
    user_profile_photo_small = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    video_thumb_url = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    topics = serializers.SerializerMethodField()
    mentioned_users = MentionedUserSerializer(many=True, read_only=True)
    queryset = Post.objects.filter(is_deleted=False)
    pdf_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    pdf_thumb_url = serializers.SerializerMethodField()
    audio_thumb_url = serializers.SerializerMethodField()
    link_meta_data = serializers.SerializerMethodField()
    post_type = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id','post_type', 'text', 'user_id', 'num_likes', 'num_comments', 'interest_id',
                  'user_firstname', 'user_lastname', 'user_profile_photo', 'user_cover_photo',
                  'user_profile_photo_small', 'user_profession', 'user_profession_text',
                  'image_url', 'video_url', 'video_thumb_url', 'resolution', 'liked_by',
                  'created_on', 'tags', 'topics', 'story_index', 'mentioned_users',
                  'pdf_url', 'pdf_thumb_url', 'link', 'audio_url', 'audio_thumb_url',
                  'link_meta_data', 'panaroma_type', 'is_work',
                  )

    def get_user_id(self, obj):
        user_id = obj.poster.id
        return user_id

    def get_interest_id(self, obj):
        return obj.interest.id

    def get_user_firstname(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        return up.first_name

    def get_user_lastname(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        return up.last_name

    def get_user_profile_photo(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.profile_photo:
            return up.profile_photo.url
        return ""

    def get_user_cover_photo(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.cover_photo:
            return up.cover_photo.url
        return ""

    def get_user_profile_photo_small(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.profile_photo_thumbnail:
            return up.profile_photo_thumbnail.url
        return ""

    def get_user_profession(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
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
            return None

    def get_num_likes(self, obj):
        return obj.liked_by.all().count()

    def get_topics(self, obj):
        return obj.topics.all().values_list('text', flat=True)

    def get_tags(self, obj):
        return obj.tags.all().values_list('name', flat=True)

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
        # needs to be added
        if obj.video:
            if obj.video_thumbnail:
                return obj.video_thumbnail.url
        else:
            return ""

    def get_mentioned_users(self, obj):
        comment = Comment.objects.get(id=obj._id)

        return [{'id': u.id, 'username': u.username} for u in comment.mentioned_users.all()]

    def get_pdf_url(self, obj):
        pdf = obj.pdf
        if pdf:
            return pdf.url
        return ""

    def get_pdf_thumb_url(self, obj):
        pdf_thumbnail = obj.pdf_thumbnail
        if pdf_thumbnail:
            return pdf_thumbnail.url
        return ""

    def get_audio_url(self, obj):
        audio = obj.audio
        if audio:
            return audio.url
        return ""

    def get_audio_thumb_url(self, obj):
        audio_thumbnail = obj.audio_thumbnail
        if audio_thumbnail:
            return audio_thumbnail.url
        return ""

    def get_link_meta_data(self, obj):
        return obj.link_meta_data if obj.link_meta_data else None

    def get_post_type(self, obj):
        if obj.image:
            return Post.TYPE_IMAGE
        elif obj.video:
            return Post.TYPE_VIDEO
        elif obj.audio:
            return Post.TYPE_AUDIO
        elif obj.link:
            return Post.TYPE_LINK
        elif obj.pdf:
            return Post.TYPE_PDF
        elif obj.text or not (obj.image and obj.video and obj.link and obj.text and obj.pdf):
            return Post.TYPE_TEXT


class PostSaveSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)
    topics = serializers.SerializerMethodField()
    topic_names = serializers.CharField(
        required=False, max_length=100, allow_blank=True)
    geo_location_lat = serializers.DecimalField(required=False, max_digits=9, decimal_places=6)
    geo_location_lng = serializers.DecimalField(required=False, max_digits=9, decimal_places=6)

    class Meta:
        model = Post
        read_only_fields = ('poster', 'brand', 'is_deleted',)

    def get_topics(self, obj):
        return obj.topics.all().values_list('text', flat=True)

    def validate(self, data):
        if 'geo_location_lat' in data and 'geo_location_lng' not in data:
            raise serializers.ValidationError(
                "You cannot submit geo_location_lat without geo_location_lng")
        if 'geo_location_lng' in data and 'geo_location_lat' not in data:
            raise serializers.ValidationError(
                "You cannot submit geo_location_lng without geo_location_lat")

        return data

    def validate_link_meta_data(self, data):
        if data:
            data = json.loads(data)
        return None


class PostUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('is_work',)

class StorySerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ('id', 'main_post', 'posts')

    def get_posts(self, obj):
        return PostSerializer(
            obj.posts.filter(is_deleted=False), many=True, context=self.context).data


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    user_first_name = serializers.SerializerMethodField()
    user_last_name = serializers.SerializerMethodField()
    user_profile_photo = serializers.SerializerMethodField()
    user_profile_photo_small = serializers.SerializerMethodField()

    post_id = serializers.SerializerMethodField()
    mentioned_users = MentionedUserSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'comment_text', 'user_id', 'user_username', 'user_first_name',
                  'user_last_name', 'user_profile_photo', 'user_profile_photo_small',
                  'mentioned_users', 'post_id', 'created_on'
                  )

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
            return ""
        if up.profile_photo:
            return up.profile_photo.url
        return ""

    def get_user_profile_photo_small(self, obj):
        try:
            up = obj.commented_by.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.profile_photo_thumbnail:
            return up.profile_photo_thumbnail.url
        return ""

    def get_mentioned_users(self, obj):
        comment = Comment.objects.get(id=obj._id)

        return [{'id': u.id, 'username': u.username} for u in comment.mentioned_users.all()]


class CommentSaveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment


class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share


class PostSearchSerializer(HaystackSerializerMixin, PostSerializer):
    class Meta(PostSerializer.Meta):
        search_fields = ("text", "interest_name", "post_text",
                         "created_on", "post_id", "topic_texts", "tag_names")
        field_aliases = {}
        exclude = tuple()

# for checking what's actually in the index
# class PostSearchSerializer(HaystackSerializer):
#     class Meta:
#         index_classes = [PostIndex]
#         fields = ("text", "post_text", "post_id", "interest_name", "interest_slug", "created_on", 'tag_names', 'topic_texts', 'term')
#         field_aliases = {}
#         exclude = {}
