# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-23 17:10
from __future__ import unicode_literals

from django.db import migrations, models


def copy_first_item_from_topics_to_topic(apps, schema_editor):
    Post = apps.get_model('post', 'Post')

    for post in Post.objects.all():
        if post.topics.all().count() > 0:
            post.topic = post.topics.all()[0].text
            post.save()


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0024_post_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.RunPython(copy_first_item_from_topics_to_topic,
            reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='post',
            name='topic',
            field=models.CharField(max_length=100, blank=False),
        ),
    ]
