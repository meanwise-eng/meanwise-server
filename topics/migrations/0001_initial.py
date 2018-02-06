# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-06 13:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=128, unique=True)),
                ('rejected', models.BooleanField(default=False)),
                ('alternative', models.CharField(blank=True, max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=128, unique=True)),
                ('slug', models.CharField(max_length=123, unique=True)),
                ('image_url', models.CharField(max_length=255)),
            ],
        ),
    ]