from django.contrib import admin

# Register your models here.
from .models import Job, Skill


class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'kind')

admin.site.register(Job, JobAdmin)
