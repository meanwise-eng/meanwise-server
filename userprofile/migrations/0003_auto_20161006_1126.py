# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-06 11:26
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('userprofile', '0002_auto_20160915_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='interest',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='interest',
            name='topics',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='interest',
            name='vote_count',
            field=models.IntegerField(default=0),
        ),
    ]
