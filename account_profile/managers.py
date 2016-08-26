from django.db import models

from common.utils import slugify
from common.mixins import CreateGetFromDataManagerMixin

from .constants import RelationType

class ProfileManager(models.Manager):

    def get_by_username_id(self, key):
        profile = None
        if key.isdigit():
            profile = self.get(id=int(key))
        else:
            profile = self.get(username=key)
        return profile

    def follow(self, source, target):
        # To avoid circular import
        from .models import Relation
        relation = Relation(source=source, target=target, relation_type=RelationType.FOLLOW)
        relation.save()

    def unfollow(self, source, target):
        from .models import Relation
        Relation.objects.filter(source=source, target=target, relation_type=RelationType.FOLLOW).delete()

    def like(self, source, target):
        from .models import Relation
        relation = Relation(source=source, target=target, relation_type=RelationType.LIKE)
        relation.save()

    def unlike(self, source, target):
        from .models import Relation
        Relation.objects.filter(source=source, target=target, relation_type=RelationType.LIKE).delete()

class SkillManager(models.Manager, CreateGetFromDataManagerMixin):
    pass

class LanguageManager(models.Manager, CreateGetFromDataManagerMixin):
    pass

class ProfessionManager(models.Manager, CreateGetFromDataManagerMixin):
    pass
