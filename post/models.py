from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from taggit.managers import TaggableManager
from common.utils import slugify

from django.contrib.auth.models import User

from userprofile.models import Interest

class Post(models.Model):
    interest = models.OneToOneField(Interest, db_index=True)
    image = models.ImageField(upload_to='post_images', null=True, blank=True)
    video = models.FileField(upload_to='post_videos', null=True, blank=True)
    text = models.CharField(max_length=200, null=True, blank=True)
    poster = models.OneToOneField(User, related_name='poster')
    tags = TaggableManager()
    liked_by = models.ManyToManyField(User, related_name='liked_by', blank=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "Interest id: " + str(self.id)  + " poster: " + str(self.poster)
    

class Comment(models.Model):
    post = models.OneToOneField(Post, db_index=True)
    commented_by = models.OneToOneField(User)
    comment_text = models.CharField(max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "Comment id: " + str(self.id)  + " post: " + str(self.post)
  
class Share(models.Model):
    post = models.OneToOneField(Post, db_index=True)
    message = models.CharField(max_length=128)
    shared_by = models.OneToOneField(User, related_name='shared_by')
    recepients = models.ManyToManyField(User, related_name='recepients')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return "Share id: " + str(self.id)  + " post: " + str(self.post) 

    
                                

