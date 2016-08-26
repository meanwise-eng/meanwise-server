from django.contrib import admin

from .models import Event, CourseMajor, Degree


class DegreeAdmin(admin.ModelAdmin):
    list_display = ('text', 'code', 'slug', 'created_on', 'last_updated',)
    list_filter = ('created_on', 'last_updated',)
    search_fields = ('text',)
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('text',)}


class CourseMajorAdmin(admin.ModelAdmin):
    list_display = ('text', 'slug', 'created_on',)
    list_filter = ('created_on',)
    search_fields = ('text',)
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('text',)}


class EventAdmin(admin.ModelAdmin):
    list_display = ('type', 'profile',
                    'description', 'city', 'created_on', 'deleted',)
    list_filter = ('created_on', 'updated_on', 'city', 'deleted',)
    search_fields = ('description', 'city', 'profile',)
    ordering = ('-id',)
    list_display_links = ('type',)

admin.site.register(Event, EventAdmin)
admin.site.register(Degree, DegreeAdmin)
admin.site.register(CourseMajor, CourseMajorAdmin)
