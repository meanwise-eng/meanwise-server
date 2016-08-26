from django.contrib import admin

from .models import Profile, LookingFor, Profession, Skill, ProfileImage,\
        CoverImage, Relation, Language


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'profession', 'city', 'created_on',)
    list_filter = ('profession', 'looking_for', 'skills', 'created_on',)
    search_fields = ('first_name', 'middle_name', 'last_name', 'username', 'city',)
    ordering = ('-user__id',)
    list_display_links = ('username', 'full_name',)


class LookingForAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'text', 'published', 'created_on',)
    list_filter = ('published', 'created_on',)
    search_fields = ('code', 'text',)
    ordering = ('-id',)
    list_display_links = ('text', 'code', 'id',)


class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'slug', 'created_on',)
    list_filter = ('created_on',)
    search_fields = ('text',)
    ordering = ('-id',)
    list_display_links = ('text', 'id',)
    prepopulated_fields = {'slug': ('text',)}


class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'slug', 'created_on',)
    list_filter = ('created_on',)
    search_fields = ('text',)
    ordering = ('-id',)
    list_display_links = ('text', 'id',)
    prepopulated_fields = {'slug': ('text',)}


class ProfileImageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'image', 'created_on',)
    list_filter = ('created_on',)
    ordering = ('-id',)


class CoverImageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'image', 'created_on',)
    list_filter = ('created_on',)
    ordering = ('-id',)


class RelationAdmin(admin.ModelAdmin):
    list_display = ('source', 'target', 'relation_type', 'created_on',)
    list_filter = ('relation_type', 'created_on',)
    search_fields = ('source', 'target',)
    ordering = ('-id',)


class LangaugeAdmin(admin.ModelAdmin):
    list_display = ('text', 'slug', 'created_on',)
    list_filter = ('created_on',)
    search_fields = ('text',)
    ordering = ('-id',)
    prepopulated_fields = {'slug': ('text',)}


admin.site.register(Profile, ProfileAdmin)
admin.site.register(LookingFor, LookingForAdmin)
admin.site.register(Profession, ProfessionAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(ProfileImage, ProfileImageAdmin)
admin.site.register(CoverImage, CoverImageAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Language, LangaugeAdmin)
