import json

from django.conf import settings

from common.db import redis


class EventSerializerCachedManager(object):
    def clear_cache(self, profile):
        redis.delete(self.get_cache_key(profile))

    def get_cache_key(self, profile):
        return '%s:%s:%s:%s:%s' % (getattr(settings, 'CACHE_KEY_PREFIX'),
                                   profile._meta.app_label,
                                   profile._meta.model_name,
                                   profile.id, 'timeline')

    def serialized(self, profile, serializer_class):
        '''
        As timeline is always fetched as a list its better to
        override this method.
        '''
        key = self.get_cache_key(profile)
        data = redis.get(key)
        data = json.loads(data) if data else None
        if data is None:
            from .models import Event
            events = Event.objects.live().filter(profile=profile)
            data = serializer_class(events, many=True).data
            # timeout = getattr(settings, 'CACHE_TIMEOUT', 1)
            redis.set(key, json.dumps(data))
            # 24 hours
        return data
