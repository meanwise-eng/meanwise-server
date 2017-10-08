from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from post.models import *
from boost.models import Boost
from boost.admin import BoostInline


class PostAdmin(admin.ModelAdmin):
    fields = ('interest', 'image', 'video', 'text', 'poster', 'tags',
              'mentioned_users', 'panaroma_type',
    )
    inlines = [BoostInline,]


class CommentAdmin(admin.ModelAdmin):
    pass


class ShareAdmin(admin.ModelAdmin):
    pass


class TopicAdmin(admin.ModelAdmin):
    pass


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Share, ShareAdmin)
admin.site.register(Topic, TopicAdmin)
