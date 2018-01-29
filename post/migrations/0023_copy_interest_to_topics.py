# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-23 16:57
from __future__ import unicode_literals

from django.db import migrations


def copy_interest_to_topics(apps, schema_editor):
    Post = apps.get_model('post', 'Post')
    Topic = apps.get_model('post', 'Topic')
    posts = Post.objects.filter(topics=None)

    for post in posts:
        try:
            topic = Topic.objects.get(text=post.interest.name)
        except Topic.DoesNotExist:
            topic = Topic.objects.create(text=post.interest.name)

        post.topics.add(topic)
        post.save()


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0022_auto_20180123_1158'),
    ]

    operations = [
        migrations.RunPython(copy_interest_to_topics, migrations.RunPython.noop),
    ]
