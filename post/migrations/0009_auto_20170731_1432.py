# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-31 14:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0008_auto_20170802_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='geo_location_lat',
            field=models.DecimalField(decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='geo_location_lng',
            field=models.DecimalField(decimal_places=6, max_digits=9, null=True),
        ),
    ]