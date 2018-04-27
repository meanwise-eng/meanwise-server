# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-19 05:07
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


def add_uuid(apps, schema_editor):
    UserProfile = apps.get_model('userprofile', 'UserProfile')
    for userprofile in UserProfile.objects.all():
        userprofile.profile_uuid = uuid.uuid4()
        userprofile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0015_skill_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_uuid',
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(add_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]