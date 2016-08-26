from django.utils import timezone

from rest_framework import serializers


class TimestampField(serializers.Field):
    def to_representation(self, value):
        epoch = timezone.datetime(1970, 1, 1)
        epoch = timezone.make_aware(epoch, timezone.get_current_timezone())
        return int((value - epoch).total_seconds())
