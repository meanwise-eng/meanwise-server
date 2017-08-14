# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-14 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mnotifications', '0003_auto_20170804_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('FA', 'FriendRequestAccepted'), ('FR', 'FriendRequestReceived'), ('LP', 'LikedPost'), ('CP', 'CommentedPost'), ('UK', 'Unknown'), ('PM', 'PostMentionedUser'), ('CM', 'CommentMentionedUser')], default='UK', max_length=2),
        ),
    ]
