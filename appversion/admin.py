from django.contrib import admin
from django import forms
from .models import Version


class VersionForm(forms.ModelForm):

    class Meta:
        model = Version
        fields = ['version_string', 'platform', 'status', ]


class VersionAdmin(admin.ModelAdmin):
    form = VersionForm
    list_display = ('version_string', 'platform', 'status',)
    list_filter = ('platform', 'status',)
    ordering = ('version_string',)

    actions = ['publish_version', 'deactivate_version', ]

    def publish_version(self, request, queryset):
        for version in queryset.all():
            version.publish()
            version.save()

    def deactivate_version(self, request, queryset):
        for version in queryset.all():
            version.deactivate()
            version.save()


admin.site.register(Version, VersionAdmin)
