from rest_framework import serializers

from account_profile.models import Skill
from account_profile.serializers import SkillSerializer
from common.models import Like
from common.utils import camel_case_to_snake_case
from common.fields import TimestampField

from .models import Work, Workitem
from .constants import WorkState


class WorkitemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    # info = serializers.JSONField(read_only=True)

    class Meta:
        model = Workitem
        fields = ('id', 'description', 'type', 'link',)

    def create_or_update(self, validated_data, work, instance=None):
        if not instance:
            instance = Workitem()
            instance.work = work
        for key, value in validated_data.items():
            setattr(instance, camel_case_to_snake_case(key), value)
        instance.save()
        return instance


class WorkDetailSerializer(serializers.ModelSerializer):
    '''
    Use this serializer only for work detail page. and should not be used for
    updating or editing work instance
    '''
    pass


class NotificationWorkSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='title')
    slug = serializers.CharField(source='notification_slug')
    type = serializers.SerializerMethodField()
    photo = serializers.CharField(source='cover_image_url')

    class Meta:
        model = Work
        fields = ('id', 'text', 'slug', 'type', 'photo',)

    def get_type(self, obj):
        return 'work'


class WorkSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    profileId = serializers.IntegerField(source='profile.id', read_only=True)
    slug = serializers.CharField(read_only=True)
    skills = SkillSerializer(many=True)
    workitemIds = serializers.ListSerializer(
        child=serializers.IntegerField(),
        allow_null=True,
        source='order'
    )
    viewsCount = serializers.IntegerField(source='views_count', read_only=True)
    likesCount = serializers.IntegerField(source='likes_count', read_only=True)
    commentsCount = serializers.IntegerField(source='comments_count',
                                             read_only=True)
    likedByLoggedInUser = serializers.SerializerMethodField()
    createdOn = TimestampField(source='created_on', read_only=True)
    updatedOn = TimestampField(source='last_updated', read_only=True)
    workitemTypes = serializers.SerializerMethodField()
    coverPhoto = serializers.URLField(source='cover_photo',
                                      required=False, allow_blank=True)

    class Meta:
        model = Work
        fields = ('id', 'profileId', 'title', 'slug', 'description',
                  'workitemIds', 'state', 'skills', 'likesCount',
                  'commentsCount', 'likedByLoggedInUser', 'viewsCount',
                  'createdOn', 'updatedOn', 'workitemTypes', 'coverPhoto',)

    def get_workitemTypes(self, obj):
        return [i.type for i in obj.workitems.all()]

    def get_likedByLoggedInUser(self, obj):
        return obj.liked_by_current_profile(self.context.get('profile'))


    def create_or_update(self, validated_data, profile, instance=None):
        '''
        This function should be used to create a draft work. A profile can have only
        one draft work.
        If a draft work already exists then overwrite those values and return it.
        '''
        create = False
        if not instance:
            create = True
            instance = Work()
        instance.profile = profile
        try:
            order = validated_data.pop('workitemIds')
        except KeyError as e:
            pass
        else:
            instance.order = order

        try:
            skills_data = self.validated_data.pop('skills')
        except KeyError as e:
            pass
        else:
            skills = []
            for skill_data in skills_data:
                skill = Skill.objects.create_or_get_from_data(skill_data)
                if skill:
                    skills.append(skill)
            instance.skills = skills

        if instance.state == WorkState.PUBLISHED or create:
            try:
                validated_data.pop('state')
            except KeyError as e:
                pass

        for key, value in validated_data.items():
            setattr(instance, camel_case_to_snake_case(key), value)

        if instance.state == WorkState.DRAFT:
            instance.searchable = False
        instance.save()
        return instance
