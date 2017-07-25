# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-25 10:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SeenPost',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('post_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('page_no', models.IntegerField()),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('is_expanded', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SeenPostBatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('datetime', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='seenpost',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='analytics.SeenPostBatch'),
        ),
    ]