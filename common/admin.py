from django.contrib import admin

from .models import Comment, Like


class LikeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'instance', 'profile', 'created_on',)
    list_filter = ('created_on',)
    ordering = ('-created_on',)
    list_display_links = ('__unicode__',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'text',
                    'instance', 'profile', 'created_on',)
    list_filter = ('created_on',)
    ordering = ('-created_on',)
    list_display_links = ('__unicode__',)


admin.site.register(Like, LikeAdmin)
admin.site.register(Comment, CommentAdmin)
