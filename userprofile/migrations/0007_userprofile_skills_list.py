# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-18 16:33
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0006_userprofile_profession_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='skills_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), default=[], size=None),
        ),
    ]
