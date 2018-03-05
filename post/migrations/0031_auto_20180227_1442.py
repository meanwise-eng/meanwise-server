# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-27 14:42
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0030_auto_20180225_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='processed',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='post_uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]