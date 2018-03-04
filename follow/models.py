from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Follow(models.Model):

    follower_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='follower')
    follower_id = models.CharField(max_length=36)
    follower_object = GenericForeignKey('follower_content_type', 'follower_id')

    followee_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='followee')
    followee_id = models.CharField(max_length=36)
    followee_object = GenericForeignKey('followee_content_type', 'followee_id')

    def __str__(self):
        return "{} {} follows {} {}".format(
            self.follower_content_type.model_class().__name__,
            self.follower_object.username,
            self.followee_content_type.model_class().__name__,
            self.followee_object
        )
