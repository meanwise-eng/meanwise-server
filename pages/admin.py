from django.contrib import admin

# Register your models here.
from .models import Page, Leader


class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'about')


class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'public')


admin.site.register(Leader, LeaderAdmin)
admin.site.register(Page, PageAdmin)
