# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-23 04:23
from __future__ import unicode_literals

from django.db import migrations, models


def add_profile_id(apps, schema_editor):
    Credits = apps.get_model('credits', 'Credits')
    UserProfile = apps.get_model('userprofile', 'UserProfile')

    for credit in Credits.objects.all():
        profile = UserProfile.objects.get(user__id=credit.user_id)
        credit.profile_id = profile.profile_uuid
        credit.save()


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0002_auto_20171203_2043'),
        ('userprofile', '0016_userprofile_profile_uuid'), 
    ]

    operations = [
        migrations.AddField(
            model_name='credits',
            name='profile_id',
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(add_profile_id, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='credits',
            name='profile_id',
            field=models.UUIDField(editable=False),
        ),
    ]