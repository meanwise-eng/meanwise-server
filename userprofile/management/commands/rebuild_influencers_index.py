import datetime

from time import sleep

from django.core.management.base import BaseCommand
from django.db.models import Q

from django.contrib.auth.models import User
from userprofile.models import UserFriend, UserProfile
from post.models import Post, Comment, Topic
from userprofile.documents import Influencer, influencers
from boost.models import Boost


class Command(BaseCommand):
    help = 'Regenerate the influencers index'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        userprofiles = UserProfile.objects.all()

        influencers.delete(ignore=404)
        Influencer.init()
        sleep(3)

        for userprofile in userprofiles:
            user = userprofile.user
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

            influencer.topics_overall = list(Topic.objects.filter(post__in=posts).values_list('text', flat=True))
            influencer.topics_weekly = list(Topic.objects.filter(post__in=posts).values_list('text', flat=True))

            try:
                boost = userprofile.profile_boosts.latest('boost_datetime')
                influencer.boost_value = boost.boost_value
                influencer.boost_datetime = boost.boost_datetime
            except Boost.DoesNotExist:
                pass

            influencer.save()
