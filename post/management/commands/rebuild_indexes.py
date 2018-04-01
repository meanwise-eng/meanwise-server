import datetime

from time import sleep

from django.core.management.base import BaseCommand

import elasticsearch

from post.models import Post
from post.documents import PostDocument, post as post_index


class Command(BaseCommand):
    help = 'Regenerate the elasticsearch indexes'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        post_index.delete(ignore=404)
        PostDocument.init()
        sleep(3)

        posts = Post.objects.filter(is_deleted=False, processed=True)
        for post in posts:
            post_doc = PostDocument()
            post_doc.set_from_post(post)
            post_doc.save()
