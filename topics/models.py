from django.db import models


class Topic(models.Model):

    text = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=123, unique=True)
    image_url = models.CharField(max_length=255, default=None)

    def __str__(self):
        return self.text


class NewTopic(models.Model):

    text = models.CharField(max_length=128, unique=True)
    rejected = models.BooleanField(default=False)
    alternative = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.text
