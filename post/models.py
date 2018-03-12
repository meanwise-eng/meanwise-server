from __future__ import unicode_literals
import os
import sys
import uuid

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.signals import post_save

from taggit.managers import TaggableManager
from common.utils import slugify
from moviepy.editor import *
from jsonfield import JSONField

from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.postgres.fields import JSONField as pgJSONField

from PIL import Image
from io import BytesIO
import logging
import tempfile

from meanwise_backend.eventsourced import EventSourced, Event

from mwmedia.models import MediaFile
from userprofile.models import Interest
from boost.models import Boost
from brands.models import Brand
from college.models import College

from .tasks import generate_video_thumbnail

logger = logging.getLogger('meanwise_backend.%s' % __name__)

class Topic(models.Model):
    text = models.CharField(max_length=128, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.text)


POST_TYPES = (
    ('image', 'Image'),
    ('video', 'Video'),
    ('pdf', 'PDF'),
    ('audio', 'Audio'),
    ('text', 'Text'),
    ('link', 'Link')
)
PANAROMA_TYPES = (
    ('', 'None'),
    ('equirectangular', 'Equirectangular'),
)
VISIBILITY_CHOICES = (
    ('Public', 'Public'),
    ('Friends', 'Friends'),
    ('List', 'List'),
)


class ShareList(models.Model):

    user = models.ForeignKey(User)
    share_with = JSONField()


class PostCreated(Event):
    pass


class PostLiked(Event):
    pass


class Post(models.Model, EventSourced):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_PDF = 'pdf'
    TYPE_AUDIO = 'audio'
    TYPE_TEXT = 'text'
    TYPE_LINK = 'link'

    post_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    post_type = models.CharField(max_length=5, default=None, choices=POST_TYPES, null=True)
    panaroma_type = models.CharField(max_length=15, default=None, choices=PANAROMA_TYPES, null=True, blank=True)
    text = models.CharField(max_length=200, null=True, blank=True)
    tags = TaggableManager(blank=True)
    topic = models.CharField(max_length=100, blank=False, null=False)
    geo_location_lat = models.DecimalField(null=True, max_digits=9, decimal_places=6)
    geo_location_lng = models.DecimalField(null=True, max_digits=9, decimal_places=6)
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_users', blank=True)
    link = models.URLField(max_length=1024, null=True, blank=True)
    link_meta_data = pgJSONField(blank=True, null=True)
    parent = models.ForeignKey('self', db_index=True, null=True)
    is_work = models.BooleanField()
    brand = models.ForeignKey(Brand, null=True, related_name='posts')
    college = models.ForeignKey(College, null=True, related_name='posts')
    media_ids = pgJSONField(null=True)

    interest = models.ForeignKey(Interest, db_index=True, null=True, blank=True)
    image = models.ImageField(upload_to='post_images', null=True, blank=True)
    video = models.FileField(upload_to='post_videos', null=True, blank=True)
    poster = models.ForeignKey(User, related_name='poster')
    topics = models.ManyToManyField(Topic, blank=True)
    pdf = models.FileField(upload_to='post_pdf', null=True, blank=True)
    audio = models.FileField(upload_to='post_audio', null=True, blank=True)
    boosts = GenericRelation(Boost, related_query_name='post')
    processed = models.BooleanField(default=True)

    # privacy settings
    visible_to = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='Public')
    share_list = models.ForeignKey(ShareList, null=True, blank=True)
    share_list_user_ids = JSONField(blank=True, default=[])
    allow_sharing = models.BooleanField(default=True)

    liked_by = models.ManyToManyField(User, related_name='liked_by', blank=True)
    is_deleted = models.BooleanField(default=False)
    video_height = models.IntegerField(null=True, blank=True)
    video_width = models.IntegerField(null=True, blank=True)
    video_thumbnail = models.ImageField(upload_to='post_video_thumbnails', null=True, blank=True)
    resolution = pgJSONField(null=True)
    pdf_thumbnail = models.ImageField(upload_to='post_pdf_thumbnails', null=True, blank=True)
    audio_thumbnail = models.ImageField(upload_to='post_audio_thumbnails', null=True, blank=True)
    story = models.ForeignKey('Story', db_index=True, null=True, related_name='posts')
    story_index = models.IntegerField(null=True)
    thumbnail = models.ImageField(upload_to='post_thumbnails', null=True, blank=True)

    legacy_deleted = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    OWNER_FIELD = 'poster'

    def post_thumbnail(self):
        if self.get_post_type() == Post.TYPE_IMAGE:
            if self.thumbnail:
                return self.thumbnail
            else:
                return self.image
        if self.get_post_type() == Post.TYPE_VIDEO:
            return self.video_thumbnail
        if self.get_post_type() == Post.TYPE_PDF:
            return self.pdf_thumbnail
        if self.get_post_type() == Post.TYPE_AUDIO:
            return self.audio_thumbnail
        return None

    def get_post_type(self):
        if self.post_type:
            return self.post_type
        if self.image:
            return Post.TYPE_IMAGE
        if self.video:
            return Post.TYPE_VIDEO
        if self.pdf_thumbnail:
            return Post.TYPE_PDF
        if self.audio_thumbnail:
            return Post.TYPE_AUDIO
        if self.link:
            return Post.TYPE_LINK
        return Post.TYPE_TEXT

    def thumbnail_required(self):
        if self.get_post_type() == Post.TYPE_TEXT:
            return False

        return True

    def __str__(self):
        return "Post id: " + str(self.id) + " poster: " + str(self.poster)

    def like(self, user):
        if user in self.liked_by.all():
            return

        self.liked_by.add(user)

        self._apply(PostLiked(self.post_uuid, 'PostLiked', {'liked_by': user.id}))

    def _apply_PostLiked(self, event: PostLiked):
        pass

    def save(self, *args, **kwargs):
        if self.id is None:
            self._apply(PostCreated(self.post_uuid, 'PostCreated', {}))

        inserting = self.post_uuid is None

        if self.post_uuid is None:
            self.post_uuid = uuid.uuid4()

        try:
            brand = Brand.objects.get(members__user=self.poster)
            self.brand = brand
        except Brand.DoesNotExist:
            pass

        colleges = College.objects.filter(featured_students__student=self.poster)
        if colleges.count() > 0:
            self.college = colleges[0]

        if inserting and self.video:
            if not self.video_thumbnail:
                super(Post, self).save(*args, **kwargs)
                try:
                    filename = os.path.splitext(os.path.basename(self.video.name))[0]
                    ext = os.path.splitext(os.path.basename(self.video.name))[-1]
                    with tempfile.NamedTemporaryFile('r+b', suffix=ext) as vf:
                        for chunk in self.video.chunks():
                            vf.write(chunk)
                        vf.seek(0)

                        clip = VideoFileClip(vf.name)
                        with tempfile.NamedTemporaryFile('r+b', suffix='.jpg') as tmp_thumb_file:
                            clip.save_frame(tmp_thumb_file.name , t=1.00)
                            _file = File(tmp_thumb_file)
                            self.video_thumbnail.save((os.path.splitext(os.path.basename(self.video.name))[0] + ".jpg"), _file, save=True)


                    self.resolution = {
                        'height': self.video_thumbnail.height,
                        'width': self.video_thumbnail.width
                    }
                except Exception as e:
                    logger.exception(e)
                    print ("Error generating video thumb", e, str(e))

            if self.video_thumbnail:
                self.resolution = {
                    'height': self.video_thumbnail.height,
                    'width': self.video_thumbnail.width
                }

        if inserting and self.image:
            im = Image.open(self.image)
            output = BytesIO()
            im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
            self.image = InMemoryUploadedFile(
                output, 'ImageField', self.image.name, 'image/jpeg', sys.getsizeof(output), None)

            self.resolution = {
                'height': self.image.height,
                'width': self.image.width
            }

            # targetting half of iPhone retina display
            target_width = 750 * 0.5
            scaling_ratio = target_width / im.width
            thumb = im.resize((int(im.width*scaling_ratio), int(im.height*scaling_ratio)),
                              Image.BICUBIC)
            thumb_output = BytesIO()
            thumb.save(thumb_output, format='JPEG', quality=95, optimize=True, progressive=True)
            self.thumbnail = InMemoryUploadedFile(thumb_output, 'ImageField', self.image.name,
                'image/jpeg', sys.getsizeof(thumb_output), None)

        super(Post, self).save(*args, **kwargs)

        if self.media_ids is None:
            media_id = None
            if self.get_post_type() == Post.TYPE_VIDEO:
                media_id = "%s/%s" % (Post.video.field.upload_to, self.video.name)
            elif self.get_post_type() == Post.TYPE_IMAGE:
                media_id = "%s/%s" % (Post.image.field.upload_to, self.image.name)

            if media_id:
                self.media_ids = [{
                    'media_id': media_id,
                    'type': self.get_post_type()
                }]

                media = MediaFile(filename=media_id, storage=MediaFile.STORAGE_S3, orphan=False)
                media.save()

                super(Post, self).save(*args, **dict(kwargs, update_fields=['media_ids'], force_insert=False))

        #if self.video and not self.video_thumbnail:
        #    generate_video_thumbnail.apply_async((self.id,), countdown=1)

        if inserting and self.poster.userprofile.post_boost:
            boost = Boost(
                boost_value = self.poster.userprofile.post_boost,
                content_object = self
            )
            boost.save()

            post_save.send(Post, instance=self, created=False)

    def num_likes(self):
        return self.liked_by.all().distinct().count()

    def num_comments(self):
        return self.comment_set.all().distinct().count()

    def rank_post_value(self):
        value = self.num_likes() + self.num_comments()
        return value


class Story(models.Model):
    main_post = models.ForeignKey(Post, db_index=True, related_name='+')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "Story id: " + str(self.id) + " main post: " + str(self.main_post)


class Comment(models.Model):
    post = models.ForeignKey(Post, db_index=True, related_name='comments')
    commented_by = models.ForeignKey(User)
    comment_text = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    mentioned_users = models.ManyToManyField(
        User, related_name='comment_mentioned_users', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Comment id: " + str(self.id) + " post: " + str(self.post)


class Share(models.Model):
    post = models.OneToOneField(Post, db_index=True)
    message = models.CharField(max_length=128)
    shared_by = models.OneToOneField(User, related_name='shared_by')
    recepients = models.ManyToManyField(User, related_name='recepients')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Share id: " + str(self.id) + " post: " + str(self.post)


class TrendingTopicsInterest(models.Model):
    interest = models.ForeignKey(Interest)
    topics = JSONField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Interest name: " + str(self.interest.name) + " topics: " + str(self.topics)


class UserTopic(models.Model):
    user = models.ForeignKey(User)
    topic = models.CharField(max_length=128)
    interest = models.CharField(max_length=128, null=True, blank=True)
    popularity = models.IntegerField()
    top_posts = pgJSONField()
    is_work = models.NullBooleanField()
