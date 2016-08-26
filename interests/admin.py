from django.contrib import admin

from .models import Interest


class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'description',
                    'created_on', 'modified_on',)
    list_filter = ('created_on', 'modified_on')
    search_fields = ('name', 'description',)
    ordering = ('-id', '-created_on',)
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin:
            return ()
        return ('slug',)

admin.site.register(Interest, InterestAdmin)
