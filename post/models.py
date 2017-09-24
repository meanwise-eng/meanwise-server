from __future__ import unicode_literals
import os
import sys

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

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

class Topic(models.Model):
    text = models.CharField(max_length=128, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Topic id: " + str(self.id) + " text: " + str(self.text)


class Post(models.Model):
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

    parent = models.ForeignKey('self', db_index=True, null=True)
    story = models.ForeignKey('Story', db_index=True, null=True, related_name='posts')
    story_index = models.IntegerField(null=True)

    boosts = GenericRelation(Boost, related_query_name='posts')

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    OWNER_FIELD = 'poster'

    def __str__(self):
        return "Post id: " + str(self.id) + " poster: " + str(self.poster)

    def save(self, *args, **kwargs):
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
    post = models.ForeignKey(Post, db_index=True)
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
