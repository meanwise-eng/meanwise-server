# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-26 12:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('actor_object_id', models.CharField(max_length=255)),
                ('verb', models.CharField(choices=[('fol', 'is now following'), ('lik', 'likes'), ('com', 'commented on')], max_length=3)),
                ('target_object_id', models.CharField(blank=True, max_length=255, null=True)),
                ('action_object_object_id', models.CharField(blank=True, max_length=255, null=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={})),
                ('is_private', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('action_object_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='action_object', to='contenttypes.ContentType')),
                ('actor_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actor', to='contenttypes.ContentType')),
                ('target_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='target', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-created_on',),
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.AlterIndexTogether(
            name='activity',
            index_together=set([('verb', 'target_object_id', 'target_content_type'), ('created_on',)]),
        ),
    ]