from django.contrib import admin

from userprofile.models import *

from boost.admin import BoostInline as BaseBoostInline

class ProfessionAdmin(admin.ModelAdmin):
    pass


class InterestAdmin(admin.ModelAdmin):
    pass


class SkillAdmin(admin.ModelAdmin):
    pass


class BoostInline(BaseBoostInline):
    verbose_name = 'Profile Boost'
    verbose_name_plural = 'Profile Boosts'

class UserProfileAdmin(admin.ModelAdmin):
    inlines = [BoostInline,]


class InviteGroupAdmin(admin.ModelAdmin):
    pass


class UserFriendAdmin(admin.ModelAdmin):
    model = UserFriend
    raw_id_fields = ('friend', 'user')


class FriendRequestAdmin(admin.ModelAdmin):
    model = FriendRequest
    raw_id_fields = ('user', 'friend')


admin.site.register(UserFriend, UserFriendAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Profession, ProfessionAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(InviteGroup, InviteGroupAdmin)
