# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-01 22:34
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mnotifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
            preserve_default=False,
        ),
    ]
