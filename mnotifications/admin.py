from django.contrib import admin

from mnotifications.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Notification, NotificationAdmin)
