from django.db import models

from common.managers import LikeableManagerMixin

from .constants import WorkState


class WorkManager(models.Manager, LikeableManagerMixin):

    def draft(self, profile):
        '''
        This function fetches a draft work. Use this only is case there is a limit of
        one draft per user.
        '''
        try:
            draft = self.get(profile=profile, state=WorkState.DRAFT)
            return draft
        except models.ObjectDoesNotExist as e:
            # Dont catch MultipleObjectsReturned. let it go to logs
            pass
        return None

    def live(self):
        return self.get_queryset().exclude(state=WorkState.DELETED)

    def published(self):
        return self.get_queryset().filter(state=WorkState.PUBLISHED)
