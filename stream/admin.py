from django.contrib import admin

from .models import Activity


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'actor', 'verb',
                    'target', 'action_object',
                    'is_private', 'created_on',)
    list_filter = ('verb', 'created_on')
    ordering = ('-created_on',)
    list_display_links = ('__unicode__', 'actor',)

admin.site.register(Activity, ActivityAdmin)
