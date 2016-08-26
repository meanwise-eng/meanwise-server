from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'activity', 'actor', 'type',
                    'target', 'profile', 'action_object',
                    'read', 'created_on',)
    list_filter = ('type', 'created_on', 'read', 'read_on')
    ordering = ('-created_on',)
    list_display_links = ('__unicode__', 'actor',)

admin.site.register(Notification, NotificationAdmin)
