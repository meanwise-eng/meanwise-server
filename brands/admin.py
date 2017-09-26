from django.contrib import admin
from django import forms
from django.contrib.admin import TabularInline

from boost.admin import BoostInline

from .models import Brand, BrandMember


class MemberInline(TabularInline):
    model = BrandMember
    extra = 1


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
    inlines = [MemberInline, BoostInline, ]
    form = BrandForm


admin.site.register(Brand, BrandAdmin)
