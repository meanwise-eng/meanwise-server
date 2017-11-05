import elasticsearch
import datetime
import logging
import sendgrid
import json

from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .documents import Influencer
from post.models import Post, Comment
from userprofile.models import UserFriend, UserProfile
from boost.models import Boost

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@receiver(post_save, sender=Boost, dispatch_uid='influencers.boost_save')
def add_profile_boost(sender, **kwargs):
    boost = kwargs['instance']

    if boost.content_type.model_class() != UserProfile:
        logger.debug("Boost type didn't match: %s != %s" % (boost.content_type.model_class(), UserProfile))
        return

    userprofile = boost.content_object
    latest_boost = userprofile.profile_boosts.latest('boost_datetime')

    if boost != latest_boost:
        return

    influencer = Influencer.get_influencer(userprofile.user_id)
    influencer.boost_value = boost.boost_value
    influencer.boost_datetime = boost.boost_datetime
    influencer.save()


@receiver(post_delete, sender=Boost, dispatch_uid='influencers.boost_delete')
def delete_profile_boost(sender, **kwargs):
    boost = kwargs['instance']
    if boost.content_type.model_class() != UserProfile:
        logger.debug("Boost type didn't match: %s != %s" % (boost.content_type.model_class(), UserProfile))
        return

    userprofile = boost.content_object
    latest_boost = userprofile.profile_boosts.latest('boost_datetime')

    influencer = Influencer.get_influencer(userprofile.user_id)
    influencer.boost_value = latest_boost.boost_value
    influencer.boost_datetime = latest_boost.boost_datetime
    influencer.save()


@receiver(post_save, sender=Post, dispatch_uid='influencers.post_save')
def add_interests_and_likes(sender, **kwargs):
    if kwargs['created']:
        post = kwargs['instance']
        influencer = Influencer.get_influencer(post.poster.id)
        influencer.interests_weekly = '%s,%s' % (influencer.interests_weekly, post.interest.name)

        influencer.save()


@receiver(post_save, sender=Comment, dispatch_uid='influencers.comment_save')
def add_comment_popularity(sender, **kwargs):
    if kwargs['created']:
        comment = kwargs['instance']
        post = comment.post

        influencer = Influencer.get_influencer(post.poster.id)

        influencer.popularity_weekly = influencer.popularity_weekly + 5

        influencer.save()


@receiver(m2m_changed,
          sender=Post.liked_by.through,
          dispatch_uid='influencers.post_liked_by_added')
def add_likes(sender, **kwargs):
    post = kwargs['instance']
    influencer = Influencer.get_influencer(post.poster.id)

    influencer.popularity_weekly = influencer.popularity_weekly + 3

    influencer.save()


@receiver(post_save, sender=UserFriend, dispatch_uid='influencers.friend_added')
def add_friends(sender, **kwargs):
    user_friend = kwargs['instance']

    influencer1 = Influencer.get_influencer(user_friend.user.id)
    influencer2 = Influencer.get_influencer(user_friend.friend.id)

    influencer1.friends += 1
    influencer2.friends += 1

    influencer1.save()
    influencer2.save()


@receiver(post_save, sender=UserProfile, dispatch_uid='userprofile.registered')
def send_welcome_email(sender, **kwargs):
    if kwargs['created']:
        userprofile = kwargs['instance']
        email = userprofile.user.email
        name = userprofile.fullname()

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

        contact = {
            "email": userprofile.user.email,
            "first_name": userprofile.first_name,
            "last_name": userprofile.last_name
        }
        logger.debug(contact)
        response = sg.client.contactdb.recipients.post(request_body=[contact])
        if response.status_code == 201:
            list_id = settings.SENDGRID_NEW_USER_LIST_ID
            res_body = json.loads(response.body.decode('utf-8'))
            if len(res_body['persisted_recipients']) > 0:
                recipient_id = res_body['persisted_recipients'][0]

            response = sg.client.contactdb.lists._(list_id).recipients._(recipient_id).post()
            logger.debug("Contact added to list: %s" % (response.status_code))

        data = {
            'content': [{'type': 'text/html', 'value': 'dummy'}],
            'from': {'email': 'm@meanwise.com', 'name': 'Meanwise'},
            'personalizations': [{
                'subject': 'dummy',
                'to': [{
                    'email': email,
                    'name': name
                }]
            }],
            'template_id': '1431c751-060c-429c-80d5-7a312c81c698'
        }

        response = sg.client.mail.send.post(request_body=data)
        logger.debug("SG Response code: %s" % (response.status_code,))
