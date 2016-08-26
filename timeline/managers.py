from django.db import models

from common.mixins import CreateGetFromDataManagerMixin


class CourseMajorManager(CreateGetFromDataManagerMixin, models.Manager):
    pass


class EventManager(models.Manager):

    def live(self):
        return self.filter(deleted=False)

    def deleted(self):
        return self.filter(deleted=True)
