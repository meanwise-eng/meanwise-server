# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-03 20:43
from __future__ import unicode_literals

from django.db import migrations

from post.models import Post
from credits.models import Critic, Credits


def create_critics_for_likes(apps, scheme_editor):

    posts = Post.objects.all()
    for post in posts:
        to_user_id = post.poster.id
        skills = list(post.topics.all().values_list('text', flat=True))
        likes = 0
        for liked_by in post.liked_by.all():
            from_user_id = liked_by.id
            try:
                critic = Critic.objects.get(to_user_id=to_user_id, from_user_id=from_user_id,
                                            post_id=post.id)
            except Critic.DoesNotExist:
                critic = Critic(to_user_id=to_user_id, from_user_id=from_user_id,
                                post_id=post.id, rating=3, skills=skills, user_credits=0,
                                created_on=post.created_on)

            critic.rating=3

            critic.save()

            likes =+ 1

        for skill in (skills + ['overall']):
            try:
                credit = Credits.objects.get(user_id=to_user_id, skill=skill)
            except Credits.DoesNotExist:
                credit = Credits(user_id=to_user_id, skill=skill, credits=0)

            credit.credits += likes

            credit.save()


def empty_reverse(apps, scheme_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('credits', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_critics_for_likes, empty_reverse),
    ]
