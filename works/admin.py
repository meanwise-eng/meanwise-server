from django.contrib import admin

from .models import Work, Workitem
from .forms import WorkForm, WorkItemForm


class WorkAdmin(admin.ModelAdmin):
    form = WorkForm
    list_display = ('profile', 'title', 'created_on', 'last_updated',)
    list_filter = ('created_on', 'last_updated', 'state', 'searchable',)
    search_fields = ('title', 'description',)
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('title',)}


class WorkItemAdmin(admin.ModelAdmin):
    form = WorkItemForm
    list_display = ('work', 'type', 'link', 'created_on', 'last_updated',)
    list_filter = ('created_on', 'last_updated',)
    search_fields = ('description',)
    ordering = ('-id',)

admin.site.register(Work, WorkAdmin)
admin.site.register(Workitem, WorkItemAdmin)
