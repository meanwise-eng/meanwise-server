from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Boost(models.Model):

    boost_value = models.PositiveIntegerField()
    boost_datetime = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return "{} ({}) for {} ID: {}".format(
            self.boost_value,
            self.boost_datetime,
            self.content_type.model_class(),
            self.object_id
        )

