from django.contrib import admin

from post.models import *


class PostAdmin(admin.ModelAdmin):
    fields = ('interest', 'image', 'video', 'text', 'poster', 'tags', 'mentioned_users')


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
