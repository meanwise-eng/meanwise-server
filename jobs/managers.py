from django.db import models

from common.mixins import CreateGetFromDataManagerMixin


class JobManager(models.Manager):
    def get_recommended_jobs(self):
        pass
