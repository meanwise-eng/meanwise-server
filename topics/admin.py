from django.contrib import admin

from topics.models import Topic, NewTopic
from post.models import Post

class NewTopicAdmin(admin.ModelAdmin):
    fields = ('text',)
    actions = ['publish']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def publish(self, request, queryset):
        for new_topic in queryset:
            topic = Topic(text=new_topic.text, slug=new_topic.text.upper())
            for post in Post.objects.filter(topic=new_topic.text, is_deleted=False).order_by('-created_on'):
                if post.post_thumbnail() is not None:
                    topic.image_url = post.post_thumbnail().url
                    break

            if topic.image_url is None:
                raise Exception("No post for this topic has an image")

            topic.save()
            new_topic.delete()

class TopicAdmin(admin.ModelAdmin):
    fields = ('text', 'slug', 'image_url',)

admin.site.register(NewTopic, NewTopicAdmin)
admin.site.register(Topic, TopicAdmin)
