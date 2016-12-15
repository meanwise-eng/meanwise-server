from django.contrib import admin

from userprofile.models import *


class ProfessionAdmin(admin.ModelAdmin):
    pass


class InterestAdmin(admin.ModelAdmin):
    pass


class SkillAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    pass

class UserFriendAdmin(admin.ModelAdmin):
    pass

class InviteGroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(Profession, ProfessionAdmin)
admin.site.register(Interest, InterestAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserFriend, UserFriendAdmin)
admin.site.register(InviteGroup, InviteGroupAdmin)

