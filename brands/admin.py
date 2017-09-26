from django.contrib import admin
from django import forms

from boost.admin import BoostInline

from .models import Brand


class BrandForm(forms.ModelForm):

    class Meta:
        model = Brand
        exclude = ('logo_thumbnail', )
        widgets = {
            'description': forms.Textarea()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_image'].required = False
        self.fields['compact_display_image'].help_text = "This will be displayed in the explore screen"


class BrandAdmin(admin.ModelAdmin):
    inlines = [BoostInline, ]
    form = BrandForm


admin.site.register(Brand, BrandAdmin)
