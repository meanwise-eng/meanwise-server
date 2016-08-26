from django.db import models
from django.contrib.contenttypes.models import ContentType


class LikeableManagerMixin(object):
    '''
    This is a generic class that provides operations on likes.
    This should also take care of cache, currently specific to works.
    '''

    def like(self, instance, profile):
        '''
        This function is used to perform like on an instance.
        '''
        from .models import Like
        like, created = Like.objects.get_or_create(
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id,
                    profile=profile)

    def unlike(self, instance, profile):
        '''
        This function is used to remove a like on an instance
        '''
        from .models import Like
        Like.objects.filter(
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id,
                    profile=profile
                ).delete()
