# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-23 13:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_auto_20170411_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False))
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='post.Post'),
        ),
        migrations.AddField(
            model_name='post',
            name='story_index',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='story',
            name='main_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='post.Post'),
        ),
        migrations.AddField(
            model_name='post',
            name='story',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='post.Story'),
        ),
    ]
