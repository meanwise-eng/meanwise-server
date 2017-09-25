from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Boost


class BoostInline(GenericTabularInline):
    model = Boost
    extra = 1
    readonly_fields = ('boost_datetime',)

