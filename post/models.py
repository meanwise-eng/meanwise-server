from __future__ import unicode_literals
import os
import sys

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

from userprofile.models import Interest
from boost.models import Boost
from brands.models import Brand

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


class Post(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_PDF = 'pdf'
    TYPE_AUDIO = 'audio'
    TYPE_TEXT = 'text'
    TYPE_LINK = 'link'

    post_type = models.CharField(max_length=5, default=None, choices=POST_TYPES, null=True)
    panaroma_type = models.CharField(max_length=15, default=None, choices=PANAROMA_TYPES, null=True, blank=True)
    interest = models.ForeignKey(Interest, db_index=True)
    image = models.ImageField(upload_to='post_images', null=True, blank=True)
    video = models.FileField(upload_to='post_videos', null=True, blank=True)
    text = models.CharField(max_length=200, null=True, blank=True)
    poster = models.ForeignKey(User, related_name='poster')
    tags = TaggableManager(blank=True)
    topics = models.ManyToManyField(Topic, blank=True)
    liked_by = models.ManyToManyField(User, related_name='liked_by', blank=True)
    is_deleted = models.BooleanField(default=False)
    video_height = models.IntegerField(null=True, blank=True)
    video_width = models.IntegerField(null=True, blank=True)
    video_thumbnail = models.ImageField(upload_to='post_video_thumbnails', null=True, blank=True)
    resolution = pgJSONField(null=True)
    geo_location_lat = models.DecimalField(null=True, max_digits=9, decimal_places=6)
    geo_location_lng = models.DecimalField(null=True, max_digits=9, decimal_places=6)
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_users', blank=True)
    pdf = models.FileField(upload_to='post_pdf', null=True, blank=True)
    pdf_thumbnail = models.ImageField(upload_to='post_pdf_thumbnails', null=True, blank=True)
    audio = models.FileField(upload_to='post_audio', null=True, blank=True)
    audio_thumbnail = models.ImageField(upload_to='post_audio_thumbnails', null=True, blank=True)
    link = models.URLField(max_length=1024, null=True, blank=True)
    link_meta_data = pgJSONField(blank=True, null=True)
    parent = models.ForeignKey('self', db_index=True, null=True)
    story = models.ForeignKey('Story', db_index=True, null=True, related_name='posts')
    story_index = models.IntegerField(null=True)
    is_work = models.BooleanField()

    boosts = GenericRelation(Boost, related_query_name='post')
    brand = models.ForeignKey(Brand, null=True, related_name='posts')

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    OWNER_FIELD = 'poster'

    def post_thumbnail(self):
        if self.get_post_type() == Post.TYPE_IMAGE:
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
        if self.video_thumbnail:
            return Post.TYPE_VIDEO
        if self.pdf_thumbnail:
            return Post.TYPE_PDF
        if self.audio_thumbnail:
            return Post.TYPE_AUDIO
        if self.link:
            return Post.TYPE_LINK
        return Post.TYPE_TEXT

    def __str__(self):
        return "Post id: " + str(self.id) + " poster: " + str(self.poster)

    def save(self, *args, **kwargs):
        inserting = self.pk is None

        try:
            brand = Brand.objects.get(members__user=self.poster)
            self.brand = brand
        except Brand.DoesNotExist:
            pass

        if self.video:
            if not self.video_thumbnail:
                super(Post, self).save(*args, **kwargs)
                try:
                    clip = VideoFileClip(self.video.path)
                    thumbnail_path = os.path.join(os.path.dirname(self.video.path), os.path.splitext(
                        os.path.basename(self.video.name))[0]) + ".jpg"
                    clip.save_frame(thumbnail_path, t=1.00)
                    _file = File(open(thumbnail_path, "rb"))
                    self.video_thumbnail.save(
                        (os.path.splitext(os.path.basename(self.video.name))[0] + ".jpg"), _file, save=True)

                    self.resolution = {
                        'height': self.video_thumbnail.height,
                        'width': self.video_thumbnail.width
                    }
                except Exception as e:
                    print ("Error generating video thumb", e, str(e))
                return

            if self.video_thumbnail:
                self.resolution = {
                    'height': self.video_thumbnail.height,
                    'width': self.video_thumbnail.width
                }

        if self.image:
            im = Image.open(self.image)
            output = BytesIO()
            im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
            self.image = InMemoryUploadedFile(
                output, 'ImageField', self.image.name, 'image/jpeg', sys.getsizeof(output), None)

            self.resolution = {
                'height': self.image.height,
                'width': self.image.width
            }

        super(Post, self).save(*args, **kwargs)

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
    interest = models.CharField(max_length=128)
    popularity = models.IntegerField()
