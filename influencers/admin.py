from django.contrib import admin
from easy_select2 import select2_modelform

from .models import Influencer

from boost.admin import BoostInline


InfluencerForm = select2_modelform(Influencer, attrs={'width': '400px'})


class InfluencerAdmin(admin.ModelAdmin):
    form = InfluencerForm
    inlines = [BoostInline,]

admin.site.register(Influencer, InfluencerAdmin)
