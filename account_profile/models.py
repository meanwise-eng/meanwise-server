from __future__ import unicode_literals

from django.db import models
from django.contrib import auth
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save, post_delete

from easy_thumbnails.fields import ThumbnailerImageField
from hitcount.models import HitCount

from allauth.models import User
from stream.constants import VerbType
from stream.utils import create as create_activity, delete as delete_activity
from common.utils import slugify, RandomFileName
from common.cache import SerializerCached, SerializerCacheManager

from .constants import OnboardingStage, RelationType
from .managers import ProfileManager, SkillManager, LanguageManager, ProfessionManager

class LookingFor(models.Model):
    text        = models.CharField(max_length=128)
    code        = models.CharField(max_length=3, unique=True)
    published   = models.BooleanField(default=False)
    created_on  = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.text

class Profession(models.Model):
    text        = models.CharField(max_length=128)
    slug        = models.SlugField(max_length=70, unique=True)
    created_on  = models.DateTimeField(auto_now_add=True)
    last_updated= models.DateTimeField(auto_now=True)
    searchable  = models.BooleanField(default=True)

    objects = ProfessionManager()
    cache   = SerializerCacheManager()

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = slugify(self.text)
        super(Profession, self).save(*args, **kwargs)

class Skill(models.Model):
    text        = models.CharField(max_length=128)
    lower      = models.CharField(max_length=128, blank=True)
    slug        = models.SlugField(max_length=70, unique=True, blank=True)
    created_on  = models.DateTimeField(auto_now_add=True)
    last_updated= models.DateTimeField(auto_now=True)
    searchable  = models.BooleanField(default=True)

    objects = SkillManager()

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.text = self.text.lower()
            self.slug = slugify(self.text)
        if not self.lower:
            self.lower = self.text.lower()
        super(Skill, self).save(*args, **kwargs)


class ProfileImage(models.Model):
    image       = ThumbnailerImageField(upload_to=RandomFileName('profile_photos'))
    created_on  = models.DateTimeField(auto_now_add=True)


class CoverImage(models.Model):
    image       = ThumbnailerImageField(upload_to=RandomFileName('cover_photos'))
    created_on  = models.DateTimeField(auto_now_add=True)


class Language(models.Model):
    text        = models.CharField(max_length=64)
    slug        = models.SlugField(max_length=70, unique=True)
    created_on  = models.DateTimeField(auto_now_add=True)
    last_updated= models.DateTimeField(auto_now=True)
    searchable  = models.BooleanField(default=True)

    objects = LanguageManager()

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = slugify(self.text)
        super(Language, self).save(*args, **kwargs)

class Profile(SerializerCached, models.Model):
    user            = models.OneToOneField(User, models.DO_NOTHING, db_index=True, null=True)
    username        = models.CharField(max_length=25, db_index=True)
    first_name      = models.CharField(max_length=128)
    middle_name     = models.CharField(max_length=128, blank=True)
    last_name       = models.CharField(max_length=128, blank=True)
    message         = models.CharField(max_length=140, blank=True)
    description     = models.CharField(max_length=1024, blank=True)
    onboarding_stage= models.CharField(max_length=2,
            choices=OnboardingStage.choices(),
            default=OnboardingStage.USERNAME)
    looking_for     = models.ForeignKey('LookingFor', models.DO_NOTHING, blank=True, null=True)
    profession      = models.ForeignKey('Profession', models.DO_NOTHING, blank=True, null=True)
    city            = models.ForeignKey('geography.City', models.DO_NOTHING, blank=True, null=True, db_index=True)
    skills          = models.ManyToManyField('Skill', related_name='profiles', blank=True)
    interests       = models.ManyToManyField('interests.Interest', related_name='interests', blank=True)
    profile_photo   = models.OneToOneField(ProfileImage, related_name='profile', blank=True, null=True)
    cover_photo     = models.OneToOneField(CoverImage, related_name='profile', blank=True, null=True)
    related         = models.ManyToManyField('Profile', through='Relation', symmetrical=False)
    languages       = models.ManyToManyField('Language', related_name='profiles', blank=True)
    created_on      = models.DateTimeField(auto_now_add=True, db_index=True)
    last_updated    = models.DateTimeField(auto_now=True, db_index=True)
    hit_count       = GenericRelation(HitCount, object_id_field='object_pk', related_query_name='hit_count_relation')

    links           = ArrayField(models.CharField(max_length=100), default=[], blank=True)

    objects         = ProfileManager()

    def __unicode__(self):
        return '%s %s (%s)' % (self.first_name, self.last_name, self.username)

    @property
    def full_name(self):
        return '%s %s %s' % (self.first_name, self.middle_name, self.last_name)

    @property
    def email(self):
        return self.user.email

    @property
    def profile_photo_url(self):
        if self.profile_photo:
            return self.profile_photo.image.url
        else:
            return settings.PROFILE_PHOTO_STUB

    @property
    def cover_photo_url(self):
        if self.cover_photo:
            return self.cover_photo.image.url
        else:
            return settings.COVER_PHOTO_STUB

    @property
    def profile_views(self):
        return self.hit_count.get().hits

    @property
    def followers(self):
        if not hasattr(self, '_followers'):
            profiles = []
            for relation in self.target.filter(
                    relation_type=RelationType.FOLLOW
                    ).select_related('source'):
                profiles.append(relation.source)
            self._followers = profiles
        return self._followers

    @property
    def follower_ids(self):
        return [p.id for p in self.followers]

    @property
    def follower_count(self):
        return len(self.followers)

    @property
    def followings(self):
        if not hasattr(self, '_followings'):
            profiles = []
            for relation in self.relation.filter(
                        relation_type=RelationType.FOLLOW
                    ).select_related('target'):
                profiles.append(relation.target)
            self._followings = profiles
        return self._followings

    @property
    def following_ids(self):
        return [p.id for p in self.followings]

    @property
    def following_count(self):
        return len(self.followings)

    @property
    def liked_by(self):
        if not hasattr(self, '_liked_by'):
            profiles = []
            for relation in self.target.filter(
                        relation_type=RelationType.LIKE
                    ).select_related('source'):
                profiles.append(relation.source)
            self._liked_by = profiles
        return self._liked_by

    @property
    def liked_by_ids(self):
        return [p.id for p in self.liked_by]

    @property
    def like_count(self):
        return len(self.liked_by)

    @property
    def likes(self):
        if not hasattr(self, '_likes'):
            profiles = []
            for relation in self.relation.filter(
                        relation_type=RelationType.LIKE
                    ).select_related('target'):
                profiles.append(relation.target)
            self._likes = profiles
        return self._likes

    @property
    def liked_ids(self):
        return [p.id for p in self.likes]


class Relation(models.Model):
    source          = models.ForeignKey(Profile, related_name='relation')
    target          = models.ForeignKey(Profile, related_name='target')
    relation_type   = models.CharField(max_length=2, choices=RelationType.choices(),
                            default=RelationType.FOLLOW)
    created_on      = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('source', 'target', 'relation_type',),)
        index_together = (
                    ('source', 'relation_type'),
                    ('target', 'relation_type')
                )

    def __unicode__(self):
        return '%s %s %s' % (self.source, self.relation_type, self.target)


def post_profile_save(sender, instance, **kwargs):
    # For now only update cache
    from .serializers import NotificationProfileSerializer, DefaultProfileDetailSerializer
    Profile.cache.serialized(instance, DefaultProfileDetailSerializer, force_fetch=True)
    Profile.cache.serialized(instance, NotificationProfileSerializer, force_fetch=True)


def post_relation_save(sender, instance, created=False, **kwargs):
    if instance.relation_type == RelationType.FOLLOW and created:
        create_activity(instance.source, verb=VerbType.FOLLOWED, target=instance.target)
    elif instance.relation_type == RelationType.LIKE and created:
        create_activity(instance.source, verb=VerbType.LIKED, target=instance.target)

    # Remove both profiles from cache
    from .serializers import DefaultProfileDetailSerializer
    Profile.cache.serialized(instance.source, DefaultProfileDetailSerializer, force_fetch=True)
    Profile.cache.serialized(instance.target, DefaultProfileDetailSerializer, force_fetch=True)

def post_relation_delete(sender, instance, **kwargs):
    if instance.relation_type == RelationType.FOLLOW:
        delete_activity(instance.source, verb=VerbType.FOLLOWED, target=instance.target)
    elif instance.relation_type == RelationType.LIKE:
        delete_activity(instance.source, verb=VerbType.LIKED, target=instance.target)
    # Remove both profiles from cache
    from .serializers import DefaultProfileDetailSerializer
    Profile.cache.serialized(instance.source, DefaultProfileDetailSerializer, force_fetch=True)
    Profile.cache.serialized(instance.target, DefaultProfileDetailSerializer, force_fetch=True)

post_save.connect(post_profile_save, sender=Profile)
post_save.connect(post_relation_save, sender=Relation)
post_delete.connect(post_relation_delete, sender=Relation)
