from __future__ import unicode_literals
import os

from django.db import models
from django.conf import settings

from taggit.managers import TaggableManager
from common.utils import slugify
from moviepy.editor import *

from django.contrib.auth.models import User
from django.core.files import File

from userprofile.models import Interest

class Topic(models.Model):
    text = models.CharField(max_length=128, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Topic id: " + str(self.id)  + " text: " + str(self.text)

class Post(models.Model):
    interest = models.ForeignKey(Interest, db_index=True)
    image = models.ImageField(upload_to='post_images', null=True, blank=True)
    video = models.FileField(upload_to='post_videos', null=True, blank=True)
    text = models.CharField(max_length=200, null=True, blank=True)
    poster = models.ForeignKey(User, related_name='poster')
    tags = TaggableManager()
    topics = models.ManyToManyField(Topic, blank=True)
    liked_by = models.ManyToManyField(User, related_name='liked_by', blank=True)
    is_deleted = models.BooleanField(default=False)
    video_height = models.IntegerField(null=True, blank=True)
    video_width = models.IntegerField(null=True, blank=True)
    video_thumbnail = models.ImageField(upload_to='post_video_thumbnails', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Post id: " + str(self.id)  + " poster: " + str(self.poster)

    def save(self, *args, **kwargs):
        if self.video:
            if not self.video_thumbnail:
                super(Post, self).save(*args, **kwargs)
                try:
                    clip = VideoFileClip(self.video.path)
                    thumbnail_path = os.path.join(os.path.dirname(self.video.path), os.path.splitext(os.path.basename(self.video.name))[0]) + ".jpg"
                    clip.save_frame(thumbnail_path , t=1.00)
                    _file = File(open(thumbnail_path, "rb"))
                    self.video_thumbnail.save((os.path.splitext(os.path.basename(self.video.name))[0] + ".jpg"), _file, save=True)
                except Exception as e:
                    print ("Error generating video thumb", e, str(e))
                return
            
        super(Post, self).save(*args, **kwargs)

    def num_likes(self):
        return self.liked_by.all().distinct().count()

    def num_comments(self):
        return self.comment_set.all().distinct().count()

    def rank_post_value(self):
        value = self.num_likes()  + self.num_comments()
        return value
  
class Comment(models.Model):
    post = models.ForeignKey(Post, db_index=True)
    commented_by = models.ForeignKey(User)
    comment_text = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Comment id: " + str(self.id)  + " post: " + str(self.post)
  
class Share(models.Model):
    post = models.OneToOneField(Post, db_index=True)
    message = models.CharField(max_length=128)
    shared_by = models.OneToOneField(User, related_name='shared_by')
    recepients = models.ManyToManyField(User, related_name='recepients')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Share id: " + str(self.id)  + " post: " + str(self.post)

