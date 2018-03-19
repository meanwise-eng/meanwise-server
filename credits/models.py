from django.db import models

from django.contrib.postgres.fields import JSONField


class Critic(models.Model):

    from_user_id = models.UUIDField()
    to_user_id = models.UUIDField()
    post_id = models.UUIDField()
    rating = models.IntegerField()
    user_credits = models.IntegerField()

    created_on = models.DateTimeField()

    skills = JSONField()


class Credits(models.Model):

    user_id = models.UUIDField()
    skill = models.CharField(max_length=256)
    credits = models.IntegerField()
