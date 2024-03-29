# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-26 12:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account_profile', '0002_auto_20160826_1213'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=255)),
                ('text', models.CharField(max_length=1024)),
                ('deleted', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_query_name='comments', to='contenttypes.ContentType')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account_profile.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='contenttypes.ContentType')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account_profile.Profile')),
            ],
        ),
    ]
