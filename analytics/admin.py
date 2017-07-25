from django.contrib import admin
from .models import SeenPost, SeenPostBatch


class SeenPostAdmin(admin.ModelAdmin):
    pass


class SeenPostBatchAdmin(admin.ModelAdmin):
    pass


admin.site.register(SeenPost, SeenPostAdmin)
admin.site.register(SeenPostBatch, SeenPostBatchAdmin)
