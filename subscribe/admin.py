from django.contrib import admin
from django.utils import timezone

from mails.mail_types import InviteMail

from .models import Invite, InviteCode


class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'created_on', 'updated_on',)
    list_filter = ('created_on', 'updated_on',)
    search_fields = ('code',)


class InviteAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'code',
                    'created_on', 'used_on', 'invited_on',)
    list_filter = ('created_on', 'used_on', 'invited_on',)
    search_fields = ('email', 'username', 'code',)
    ordering = ('-id', '-created_on',)
    list_display_links = ('id', 'email', 'code',)
    actions = ('send_invite_mail',)

    def send_invite_mail(self, request, queryset):
        for invite in queryset:
            email = invite.email
            token = invite.code
            invite_mail = InviteMail(email, {'code': token})
            invite_mail.send()
            invite.invited_on = timezone.now()
            invite.save()


admin.site.register(Invite, InviteAdmin)
admin.site.register(InviteCode, InviteCodeAdmin)
