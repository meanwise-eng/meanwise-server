from django.db import models

from django.contrib.contenttypes.fields import GenericRelation

from boost.models import Boost
from userprofile.models import UserProfile


class Influencer(models.Model):

    userprofile = models.ForeignKey(UserProfile)
    boosts = GenericRelation(Boost, related_query_name='influencer')
