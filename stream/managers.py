from django.db import models
from django.contrib.contenttypes.models import ContentType


class ActivityManager(models.Manager):
    '''
    This implements methods for making querying on activity easier
    '''
    def by_target(self, target):
        target_content_type = ContentType.objects.get_for_model(target)
        return self.filter(target_content_type=target_content_type,
                           target_object_id=target.id,
                           is_private=False
                           )
