import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q

from django.contrib.auth.models import User
from userprofile.models import UserFriend
from post.models import Post, Comment
from userprofile.documents import Influencer, influencers


class Command(BaseCommand):
    help = 'Regenerate the influencers index'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        users = User.objects.all()

        influencers.delete(ignore=404)

        for user in users:
            influencer = Influencer.get_influencer(user.id)

            influencer.friends = UserFriend.objects.filter(
                Q(user=user) | Q(friend=user)
            ).count()

            posts = Post.objects.filter(poster=user)

            one_week_ago = datetime.datetime.now() - datetime.timedelta(weeks=1)

            for post in posts:
                old_comments_count = Comment.objects.filter(post=post)\
                    .filter(created_on__lt=one_week_ago).count()
                weekly_comments_count = Comment.objects.filter(post=post)\
                    .filter(created_on__gte=one_week_ago).count()

                likes = post.liked_by.count()

                influencer.popularity_weeky = (weekly_comments_count * 5)
                influencer.popularity_overall = (old_comments_count * 5) + (likes * 3)

            influencer.interests_overall = ','.join(posts.filter(
                created_on__lt=one_week_ago).values_list('interest__name', flat=True))
            influencer.interests_weekly = ','.join(posts.filter(
                created_on__gte=one_week_ago).values_list('interest__name', flat=True))

            influencer.save()
