# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-01 20:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mnotifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='post_mentioned_users',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_mentioned_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
