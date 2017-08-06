from django.contrib import admin

from .models import Location, City


class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'area', 'country',
                    'place_id', 'created_on',)
    list_filter = ('created_on', 'country',)
    search_fields = ('description',)
    ordering = ('-id', 'country',)
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('description',)}


class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'area', 'country', 'place_id', 'created_on',)
    list_filter = ('created_on', 'country',)
    search_fields = ('description',)
    ordering = ('-id', 'country',)
    list_display_links = ('city',)
    prepopulated_fields = {'slug': ('description',)}


admin.site.register(Location, LocationAdmin)
admin.site.register(City, CityAdmin)
