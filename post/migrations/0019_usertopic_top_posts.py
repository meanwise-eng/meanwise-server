# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-26 12:31
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0018_auto_20171127_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertopic',
            name='top_posts',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=[]),
            preserve_default=False,
        ),
    ]
