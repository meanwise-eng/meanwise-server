from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone

from .utils import generate_invite_code

DAYS_FOR_INVITE_CODE_EXPIRY = settings.INVITE_CODE_EXPIRY


class InviteCode(models.Model):
    code = models.CharField(max_length=12)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.code


class Invite(models.Model):
    email = models.EmailField(max_length=128, unique=True, db_index=True)
    username = models.CharField(max_length=25, default='', db_index=True)
    code = models.CharField(max_length=24, unique=True, db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)
    used_on = models.DateTimeField(blank=True, null=True)
    invited_on = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return '%s : %s' % (self.email, self.code)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_invite_code(length=8)
        super(Invite, self).save(*args, **kwargs)

    def is_valid(self, email):
        time_delta = timezone.now() - self.created_on
        # Email dont match or invite code has expired
        if not (self.email == email) or time_delta.days > DAYS_FOR_INVITE_CODE_EXPIRY:
            return False
        return True

    def mark_registered(self):
        self.username = ''
        self.used_on = timezone.now()
        self.save()
