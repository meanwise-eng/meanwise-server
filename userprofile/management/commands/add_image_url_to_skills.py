import datetime

from time import sleep

from django.core.management.base import BaseCommand
from django.db.models import Q

from django.contrib.auth.models import User
from userprofile.models import Skill
from post.models import Post


class Command(BaseCommand):
    help = 'Generate the image urls for skills'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        skills = Skill.objects.all()

        for skill in skills:
            posts = Post.objects.filter(topics__text=skill.text).order_by('-created_on')

            for post in posts:
                if post.post_thumbnail() is not None:
                    skill.image_url = post.post_thumbnail().url
                    skill.save()
                    break
