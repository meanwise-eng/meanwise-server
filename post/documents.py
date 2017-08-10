from django_elasticsearch_dsl import DocType, Index, fields
import datetime

from analytics.models import SeenPost
from .models import Post, Comment

post = Index('mw_posts')

post.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@post.doc_type
class PostDocument(DocType):

    interest_id = fields.IntegerField()
    interest_name = fields.StringField(index='not_analyzed')
    image_url = fields.StringField()
    video_url = fields.StringField()
    user_id = fields.IntegerField()
    tags = fields.ListField(fields.StringField())
    num_likes = fields.IntegerField()
    num_recent_likes = fields.IntegerField()
    num_comments = fields.IntegerField()
    num_recent_comments = fields.IntegerField()
    user_firstname = fields.StringField()
    user_lastname = fields.StringField()
    user_profile_photo = fields.StringField()
    user_cover_photo = fields.StringField()
    user_profession_id = fields.IntegerField()
    user_profession_text = fields.StringField()
    user_profile_photo_small = fields.StringField()
    video_thumb_url = fields.StringField()
    topics = fields.ListField(fields.StringField())
    num_seen = fields.IntegerField()
    num_recent_seen = fields.IntegerField()
    created_on = fields.DateField()
    geo_location = fields.GeoPointField()

    class Meta:
        model = Post

    def prepare_interest_id(self, obj):
        return obj.interest.id

    def prepare_image(self, obj):
        if obj.image:
            return obj.image.url

    def prepare_user_id(self, obj):
        user_id = obj.poster.id
        return user_id

    def prepare_interest_id(self, obj):
        return obj.interest.id

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
