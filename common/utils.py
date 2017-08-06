import os
import uuid
import ast

from django.db import models
from slugify import slugify as _slugify, SLUG_OK

from django.utils import timezone
from django.utils.text import re_camel_case
from django.utils.dateformat import format
from django.utils.deconstruct import deconstructible


def format_error_response(data):
    messages = []
    for key in data:
        message = data[key][0]
        break
    return message


def camel_case_to_snake_case(value):
    return re_camel_case.sub(r'_\1', value).strip().lower()


def slugify(text, ok=None, **kwargs):
    if not ok:
        ok = SLUG_OK + '.'
    return _slugify(text, ok=ok, **kwargs)


def timestamp(time):
    epoch = timezone.datetime(1970, 1, 1)
    epoch = timezone.make_aware(epoch, timezone.get_current_timezone())
    return int((time - epoch).total_seconds())


@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        self.path = os.path.join(path, "%s%s")

    def __call__(self, _, filename):
        extension = os.path.splitext(filename)[1]
        return self.path % (uuid.uuid4(), extension)


class ListField(models.TextField):
    description = "Stores a list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []
        if isinstance(value, list):
            return value
        return ast.literal_eval(value)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
