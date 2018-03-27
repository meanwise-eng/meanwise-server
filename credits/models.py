from django.db import models

from django.contrib.postgres.fields import JSONField


class Critic(models.Model):

    from_user_id = models.IntegerField()
    to_user_id = models.IntegerField()
    post_id = models.IntegerField()
    rating = models.IntegerField()
    user_credits = models.IntegerField()

    created_on = models.DateTimeField()

    skills = JSONField()


class Credits(models.Model):

    user_id = models.IntegerField()
    profile_id = models.UUIDField(editable=False)
    skill = models.CharField(max_length=256)
    credits = models.IntegerField()
