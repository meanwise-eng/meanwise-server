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


class BrandAdmin(admin.ModelAdmin):
    inlines = [BoostInline, ]
    form = BrandForm


admin.site.register(Brand, BrandAdmin)
