# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-26 21:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0019_usertopic_top_posts'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertopic',
            name='is_work',
            field=models.NullBooleanField(),
        ),
    ]
