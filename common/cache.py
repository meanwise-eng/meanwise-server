import json

from django.conf import settings
from django.db import models

from common.db import redis


class SerializerCacheManager(models.Manager):

    def clear_cache(self, instance=None, serializer_class=None):
        '''
        #TODO This doesnt work. #Fixit.
        '''
        if not instance:
            key_pattern = '%s:%s:%s*' % (getattr(settings, 'CACHE_KEY_PREFIX', ''),
                                         instance._meta.app_label, instance._meta.model_name)
        elif not serializer_class:
            key_pattern = '%s:%s:%s:%s*' % (getattr(settings, 'CACHE_KEY_PREFIX', ''),
                                            instance._meta.app_label,
                                            instance._meta.model_name,
                                            instance.pk
                                            )
        else:
            key_pattern = '%s:%s:%s:%s:%s' % (getattr(settings, 'CACHE_KEY_PREFIX', ''),
                                              instance._meta.app_label,
                                              instance._meta.model_name,
                                              instance.pk,
                                              serializer_class.__name__
                                              )
        redis.delete(key_pattern)

    def get_cache_key(self, instance, serializer_class):
        return '%s:%s:%s:%s:%s' % (getattr(settings, 'CACHE_KEY_PREFIX'),
                                   instance._meta.app_label,
                                   instance._meta.model_name,
                                   instance.pk,
                                   serializer_class.__name__
                                   )

    def serialized(self, instance, serializer_class, many=False, force_fetch=False):
        '''
        This works for `many=False`
        This function checks in cache if the serialized object already exists or not
        If exists return from cache.
        If not then serialize the object and save in cache
        And return
        Force_fetch doesn't check in cache
        '''
        if many:
            return serializer_class(instance, many=True).data
        data = None
        key = self.get_cache_key(instance, serializer_class)
        if not force_fetch:
            data = redis.get(key)
            data = json.loads(data) if data else data
        if not data:
            data = serializer_class(instance).data
            # timeout = getattr(settings, 'CACHE_TIMEOUT', 1)
            redis.set(key, json.dumps(data))
        return data

    def get(self, pk, serializer_class):
        instance = self.model()
        instance.pk = pk
        key = self.get_cache_key(instance, serializer_class)
        data = redis.get(key)
        data = json.loads(data) if data else data
        instance = super(SerializerCacheManager, self).get(pk=pk)
        return self.serialized(instance, serializer_class, force_fetch=True)


class SerializerCached(object):
    cache = SerializerCacheManager()
