# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-05 14:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0026_auto_20180201_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='legacy_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
