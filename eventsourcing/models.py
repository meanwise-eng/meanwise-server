from django.db import models
from django.contrib.postgres.fields import JSONField


class Event(models.Model):

    aggregate_id = models.UUIDField(primary_key=True)
    event_id = models.IntegerField()
    stream = models.CharField(max_length=255)
    data = JSONField()
    metadata = JSONField()
    committed = models.BooleanField(default=False)
