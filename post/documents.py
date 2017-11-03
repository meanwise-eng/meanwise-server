import datetime

from elasticsearch_dsl import (Integer, String, Date, Boolean, Index, DocType, GeoPoint,)

from django.urls import reverse
from common.api_helper import build_absolute_uri

from analytics.models import SeenPost
from .models import Post, Comment

from userprofile.models import UserProfile
from boost.models import Boost

post = Index('mw_posts_2')

post.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@post.doc_type
class PostDocument(DocType):

    interest_id = Integer()
    interest_name = String(index='not_analyzed')
    text = String()
    image_url = String()
    video_url = String()
    user_id = Integer()
    tags = String()
    num_likes = Integer()
    num_recent_likes = Integer()
    num_comments = Integer()
    num_recent_comments = Integer()
    user_firstname = String()
    user_lastname = String()
    user_profile_photo = String()
    user_cover_photo = String()
    user_profession_id = Integer()
    user_profession_text = String()
    user_profile_photo_small = String()
    video_thumb_url = String()
    topics = String()
    num_seen = Integer()
    num_recent_seen = Integer()
    created_on = Date()
    geo_location = GeoPoint()
    pdf_url = String()
    audio_url = String()
    link = String()
    pdf_thumb_url = String()
    audio_thumb_url = String()
    post_type = String()
    panaroma_type = String()
    post_thumbnail_url = String()
    is_work = Boolean()

    boost_value = Integer()
    boost_datetime = Date()

    brand = String()
    brand_logo_url = String()

    class Meta:
        index = 'mw_posts_2'

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def prepare_interest_id(self, obj):
        return obj.interest.id

    def prepare_image(self, obj):
        if obj.image:
            return obj.image.url

    def prepare_user_id(self, obj):
        user_id = obj.poster.id
        return user_id

    def prepare_interest_name(self, obj):
        return obj.interest.name.lower()

    def prepare_user_firstname(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        return up.first_name

    def prepare_user_lastname(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        return up.last_name

    def prepare_user_profile_photo(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.profile_photo:
            return up.profile_photo.url
        return ""

    def prepare_user_cover_photo(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.cover_photo:
            return up.cover_photo.url
        return ""

    def prepare_user_profile_photo_small(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return ""
        if up.profile_photo_thumbnail:
            return up.profile_photo_thumbnail.url
        return ""

    def prepare_user_profession_id(self, obj):
        try:
            up = obj.poster.userprofile
        except UserProfile.DoesNotExist:
            return None
        profession = up.profession

        if not profession:
            return None

        return profession.id

    def prepare_user_profession_text(self, obj):
        try:
            up = obj.poster.userprofile
            return up.profession_text
        except UserProfile.DoesNotExist:
            return None

    def prepare_num_likes(self, obj):
        return obj.liked_by.count()

    def prepare_num_recent_likes(self, obj):
        return obj.liked_by.count()

    def prepare_topics(self, obj):
        return list(obj.topics.all().values_list('text', flat=True))

    def prepare_tags(self, obj):
        return list(obj.tags.all().values_list('name', flat=True))

    def prepare_num_comments(self, obj):
        return Comment.objects.filter(post=obj).filter(is_deleted=False)\
            .count()

    def prepare_num_recent_comments(self, obj):
        return Comment.objects.filter(post=obj).filter(is_deleted=False)\
            .filter(created_on__gte=(datetime.datetime.now() - datetime.timedelta(weeks=1)))\
            .count()

    def prepare_image_url(self, obj):
        _image = obj.image
        if _image:
            return _image.url
        return ""

    def prepare_video_url(self, obj):
        _video = obj.video
        if _video:
            return _video.url
        return None

    def prepare_video_thumb_url(self, obj):
        # needs to be added
        if obj.video:
            if obj.video_thumbnail:
                return obj.video_thumbnail.url
        else:
            return None

    def prepare_num_seen(self, obj):
        return SeenPost.objects.filter(post_id=obj.id)\
            .count()

    def prepare_num_recent_seen(self, obj):
        return SeenPost.objects.filter(post_id=obj.id)\
            .filter(datetime__gte=(datetime.datetime.now() - datetime.timedelta(weeks=1)))\
            .count()

    def prepare_geo_location(self, obj):
        if not obj.geo_location_lat:
            return None
        return {
            'lat': float(obj.geo_location_lat),
            'lon': float(obj.geo_location_lng)
        }

    def prepare_audio_url(self, obj):
        _audio = obj.audio
        if _audio:
            return _audio.url
        return None

    def prepare_pdf_url(self, obj):
        _pdf = obj.pdf
        if _pdf:
            return _pdf.url
        return None

    def prepare_link(self, obj):
        return obj.link

    def prepare_audio_thumb_url(self, obj):
        # needs to be added
        if obj.audio:
            if obj.audio_thumbnail:
                return obj.audio_thumbnail.url
        else:
            return None

    def prepare_pdf_thumb_url(self, obj):
        # needs to be added
        if obj.pdf:
            if obj.pdf_thumbnail:
                return obj.pdf_thumbnail.url
        else:
            return None

    def prepare_post_type(self, obj):
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
        elif obj.text or not (obj.image or obj.video or obj.link or obj.text or obj.pdf):
            return Post.TYPE_TEXT

    def prepare_boost_value(self, obj):
        try:
            boost = obj.boosts.latest('boost_datetime')
        except Boost.DoesNotExist:
            return None
        return boost.boost_value

    def prepare_boost_datetime(self, obj):
        try:
            boost = obj.boosts.latest('boost_datetime')
        except Boost.DoesNotExist:
            return None
        return boost.boost_datetime

    def prepare_brand(self, obj):
        if obj.brand is None:
            return None

        return build_absolute_uri(reverse('brand-details', kwargs={'brand_id': obj.brand.id}))

    def prepare_brand_logo_url(self, obj):
        if obj.brand is None:
            return None

        return obj.brand.logo_thumbnail.url

    def prepare_post_thumbnail_url(self, obj):
        return obj.post_thumbnail().url if obj.post_thumbnail() else None

    def set_from_post(self, post):
        properties = ('interest_id', 'interest_name', 'text', 'image_url', 'video_url', 'user_id', 'tags', 'num_likes', 'num_recent_likes', 'num_comments', 'num_recent_comments', 'user_firstname', 'user_lastname', 'user_profile_photo', 'user_cover_photo', 'user_profession_id', 'user_profession_text', 'user_profile_photo_small', 'video_thumb_url', 'topics', 'num_seen', 'num_recent_seen', 'created_on', 'geo_location', 'pdf_url', 'audio_url', 'link', 'pdf_thumb_url', 'audio_thumb_url', 'post_type', 'panaroma_type', 'post_thumbnail_url', 'is_work', 'boost_value', 'boost_datetime', 'brand', 'brand_logo_url')
        for key in properties:
            method = 'prepare_%s' % key
            if hasattr(self, method):
               value = getattr(self, method)(post)
            elif hasattr(post, key):
                value = getattr(post, key)
            else:
                raise Exception("Cannot get value for key %s" % key)

            setattr(self, key, value)

        self._id = post.id
