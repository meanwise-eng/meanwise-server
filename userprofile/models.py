from __future__ import unicode_literals

import sys
from PIL import Image
from io import BytesIO

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib import auth
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from taggit.managers import TaggableManager

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from common.utils import slugify

from .exceptions import AlreadyExistsError, AlreadyFriendsError


CACHE_TYPES = {
    'friends': 'f-%s',
    'requests': 'fr-%s',
    'sent_requests': 'sfr-%s',
    'rejected_requests': 'frj-%s',
    'unrejected_requests': 'frur-%s',
}

BUST_CACHES = {
    'friends': ['friends'],
    'requests': [
        'requests',
        'rejected_requests',
    ],
    'sent_requests': ['sent_requests'],
}


def cache_key(type, user_pk):
    """
    Build the cache key for a particular type of cached value
    """
    return CACHE_TYPES[type] % user_pk


def bust_cache(type, user_pk):
    """
    Bust our cache for a given type, can bust multiple caches
    """
    bust_keys = BUST_CACHES[type]
    keys = [CACHE_TYPES[k] % user_pk for k in bust_keys]
    cache.delete_many(keys)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Profession(models.Model):
    text = models.CharField(max_length=128)
    slug = models.SlugField(max_length=70, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    searchable = models.BooleanField(default=True)

    def __str__(self):
        return "Profession id: " + str(self.id) + " text : " + str(self.text)

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = slugify(self.text)
        super(Profession, self).save(*args, **kwargs)


class Skill(models.Model):
    text = models.CharField(max_length=128)
    lower = models.CharField(max_length=128, blank=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    searchable = models.BooleanField(default=True)

    def __str__(self):
        return "Skill id:" + str(self.id) + " text:" + str(self.text)

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.text = self.text.lower()
            self.slug = slugify(self.text)
        if not self.lower:
            self.lower = self.text.lower()
        super(Skill, self).save(*args, **kwargs)


class Interest(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=70, unique=True)
    description = models.CharField(max_length=128)
    published = models.BooleanField(default=False, db_index=True)
    cover_photo = models.ImageField(upload_to='interest_photos', null=True, blank=True)
    color_code = models.CharField(max_length=7, null=True, blank=True)
    topics = TaggableManager()
    is_deleted = models.BooleanField(default=False)
    vote_count = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if self.cover_photo:
            im = Image.open(self.cover_photo)
            output = BytesIO()
            im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
            self.cover_photo = InMemoryUploadedFile(
                output, 'models.ImageField', self.cover_photo.name,
                'image/jpeg', sys.getsizeof(output), None
            )

        super(Interest, self).save(*args, **kwargs)

    def __str__(self):
        return "Interest id: " + str(self.id) + " name " + str(self.name)

    @property
    def cover_photo_url(self):
        if self.cover_photo:
            return self.cover_photo.url
        else:
            return ''


class UserInterestRelevance(models.Model):
    interest = models.ForeignKey(Interest)
    user = models.ForeignKey(User)
    weekly_views = models.IntegerField()
    old_views = models.IntegerField()
    last_reset = models.DateTimeField()


class UserProfile(models.Model):

    USERTYPE_INVITED = 1
    USERTYPE_GUEST = 0

    user = models.OneToOneField(User, db_index=True)
    facebook_token = models.CharField(max_length=128, null=True, blank=True)
    username = models.CharField(max_length=25, db_index=True)
    first_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    profession = models.ForeignKey(Profession, blank=True, null=True)
    profession_text = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name='skills', blank=True)
    skills_list = ArrayField(models.CharField(max_length=128), default=list())

    interests = models.ManyToManyField(Interest,
                                       related_name='interests', blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos', blank=True)
    profile_photo_thumbnail = models.ImageField(upload_to='profile_photo_thumbs', blank=True)

    cover_photo = models.ImageField(upload_to='cover_photos', blank=True)
    bio = models.TextField(null=True, blank=True)
    intro_video = models.FileField(upload_to='intro_videos', null=True, blank=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    profile_story_title = models.CharField(max_length=255, blank=True, null=True)
    profile_story_description = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    user_type = models.IntegerField(default=int(0), null=False)
    profile_background_color = models.CharField(default='#FFFFFF', max_length=20)

    def save(self, *args, **kwargs):

        if self.cover_photo:
            im = Image.open(self.cover_photo)
            output = BytesIO()
            im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
            self.cover_photo = InMemoryUploadedFile(
                output, 'models.ImageField',
                self.cover_photo.name, 'image/jpeg',
                sys.getsizeof(output), None
            )

        if self.profile_photo:
            im = Image.open(self.profile_photo)
            output = BytesIO()
            im.save(output, format='JPEG', quality=100, optimize=True, progressive=True)
            self.profile_photo = InMemoryUploadedFile(
                output, 'models.ImageField',
                self.profile_photo.name, 'image/jpeg',
                sys.getsizeof(output), None
            )

            thumbnail_size = (48, 48)
            thumbnail_output = BytesIO()
            im.thumbnail(thumbnail_size)
            im.save(thumbnail_output, format='JPEG', quality=100, optimize=True)
            self.profile_photo_thumbnail = InMemoryUploadedFile(
                thumbnail_output,
                'models.ImageField',
                self.profile_photo.name,
                'image/jpeg',
                sys.getsizeof(thumbnail_output),
                None
            )

        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return 'user profile id %s - %s %s %s' % (str(self.id),
                                                  self.first_name,
                                                  self.last_name,
                                                  self.username
                                                  )


class FriendRequest(models.Model):
    user = models.ForeignKey(User, related_name='Friend_request_sent')
    friend = models.ForeignKey(User, related_name='Friend_request_received')

    created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Friend Request"
        verbose_name_plural = "Friend Requests"
        unique_together = ("user", "friend")

    def __str__(self):
        return "User %s friend requested %s" % (self.user, self.friend)

    def accept(self):
        """
        Accept a friend request
        """
        rel = UserFriend.objects.create(
            user=self.user,
            friend=self.friend
        )
        rel2 = UserFriend.objects.create(
            user=self.friend,
            friend=self.user
        )

        self.delete()
        FriendRequest.objects.filter(
            user=self.friend,
            friend=self.user
        ).delete()

        # Bust requests cache - request is deleted
        bust_cache('requests', self.friend.pk)
        bust_cache('sent_requests', self.user.pk)
        # Bust reverse requests cache - reverse request might be deleted
        bust_cache('requests', self.user.pk)
        bust_cache('sent_requests', self.friend.pk)
        # Bust friends cache - new friends added
        bust_cache('friends', self.friend.pk)
        bust_cache('friends', self.user.pk)

        return True

    def reject(self):
        """
        Reject a friend request
        """

        self.delete()
        bust_cache('requests', self.friend.pk)
        bust_cache('sent_requests', self.user.pk)
        return True


class FriendManager(models.Manager):
    """
    Friend Manager
    """

    def friends(self, user):
        """
        Return a list of all friends of a user
        """
        key = cache_key('friends', user.pk)
        friends = cache.get(key)

        if friends is None:
            qs = UserFriend.objects.select_related('user', 'friend').filter(friend=user).all()
            friends = [u.user for u in qs]
            # cache.set(key, friends)

        return friends

    def requests(self, user):
        """ Return a list of friend requests """
        key = cache_key('requests', user.pk)
        requests = cache.get(key)

        if requests is None:
            qs = FriendRequest.objects.select_related('user', 'friend').filter(
                friend=user).all()
            requests = list(qs)
            # cache.set(key, requests)

        return requests

    def sent_requests(self, user):
        """ Return a list of friendship requests from user """
        key = cache_key('sent_requests', user.pk)
        requests = cache.get(key)

        if requests is None:
            qs = FriendRequest.objects.filter(user=user)
            requests = list(qs)
            # cache.set(key, requests)

        return requests

    def add_friend(self, user, friend):
        """ Create a friend request """
        if user == friend:
            raise PermissionDenied("Users cannot be friends with themselves")

        if self.are_friends(user, friend):
            raise AlreadyFriendsError("Users are already friends")

        request, created = FriendRequest.objects.get_or_create(
            user=user,
            friend=friend,
        )

        if created is False:
            raise AlreadyExistsError("Friend already requested")

        bust_cache('requests', friend.pk)
        bust_cache('sent_requests', user.pk)

        return request

    def remove_friend(self, user, friend):
        """ Destroy a friend relationship """
        try:
            qs = UserFriend.objects.filter(
                Q(user=user, friend=friend) |
                Q(user=friend, friend=user)
            ).distinct().all()

            if qs:
                qs.delete()
                bust_cache('friends', friend.pk)
                bust_cache('friends', user.pk)
                return True
            else:
                return False
        except UserFriend.DoesNotExist:
            return False

    def are_friends(self, user1, user2):
        """ Are these two users friends? """
        friends1 = cache.get(cache_key('friends', user1.pk))
        friends2 = cache.get(cache_key('friends', user2.pk))
        if friends1 and user2 in friends1:
            return True
        elif friends2 and user1 in friends2:
            return True
        else:
            try:
                UserFriend.objects.get(friend=user1, user=user2)
                return True
            except UserFriend.DoesNotExist:
                return False


FRIEND_STATUS = (
    ('PE', 'Pending'),
    ('AC', 'Accepted'),
    ('RE', 'Rejected'),
)


class UserFriend(models.Model):
    STATUS_PENDING = 'PE'
    STATUS_ACCEPTED = 'AC'
    STATUS_REJECTED = 'RE'

    user = models.ForeignKey(User, related_name='user')
    friend = models.ForeignKey(User, related_name='friend')

    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=2, choices=FRIEND_STATUS, default=None, blank=True)
    objects = FriendManager()

    class Meta:
        verbose_name = "Friend"
        verbose_name_plural = "Friends"
        unique_together = ("user", "friend")

    def __str__(self):
        return 'user %sfriend %s ' % (str(self.user), str(self.friend))


class InviteGroup(models.Model):
    name = models.CharField(max_length=128)
    count = models.IntegerField(default=0)
    invite_code = models.CharField(max_length=128)
    users = models.ManyToManyField(User, blank=True)
    max_invites = models.IntegerField(default=100)

    def __str__(self):
        return 'invite group id %s - %s  count (%s)' % (str(self.id), self.name, self.count)
