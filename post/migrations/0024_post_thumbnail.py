# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-23 22:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0023_copy_interest_to_topics'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='post_thumbnails'),
        ),
    ]
