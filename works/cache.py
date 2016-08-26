import json

from django.conf import settings

from common.db import redis
from common.cache import SerializerCacheManager


class WorkSerializerCachedManager(SerializerCacheManager):
    def clear_cache(self, profile):
        redis.delete(self.get_cache_key(profile))

    def get_cache_key(self, profile):
        return '%s:%s:%s:%s:%s' % (getattr(settings, 'CACHE_KEY_PREFIX'),
                                   profile._meta.app_label,
                                   profile._meta.model_name,
                                   profile.id, 'works')

    def serialized_by_profile(self, profile, serializer_class, drafts=False, force_fetch=False):
        '''
        As timeline is always fetched as a list its better to
        override this method.
        '''
        key = self.get_cache_key(profile)
        if force_fetch:
            data = None
        else:
            data = redis.get(key)
            data = json.loads(data) if data else None
        if data is None:
            from .models import Work
            works = Work.objects.filter(profile=profile)
            data = serializer_class(works, many=True).data
            redis.set(key, json.dumps(data))
            # 24 hours
        return data
