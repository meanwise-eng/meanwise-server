import logging

from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

from .models import Influencer
from boost.models import Boost
from userprofile.documents import Influencer as InfluencerDoc

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@receiver(post_save, sender=Boost, dispatch_uid='influencers.boost_save')
def add_profile_boost(sender, **kwargs):
    boost = kwargs['instance']

    if boost.content_type.model_class() != Influencer:
        logger.debug("Boost type didn't match: %s != %s" % (boost.content_type.model_class(), Influencer))
        return

    influencer = boost.content_object
    latest_boost = influencer.boosts.latest('boost_datetime')

    if boost != latest_boost:
        return

    influencer_doc = InfluencerDoc.get_influencer(influencer.userprofile.user_id)
    influencer_doc.boost_value = boost.boost_value
    influencer_doc.boost_datetime = boost.boost_datetime
    influencer_doc.save()


@receiver(post_delete, sender=Boost, dispatch_uid='influencers.boost_delete')
def delete_profile_boost(sender, **kwargs):
    boost = kwargs['instance']

    if boost.content_type.model_class() != Influencer:
        logger.debug("Boost type didn't match: %s != %s" % (boost.content_type.model_class(), Influencer))
        return

    influencer = boost.content_object

    try:
        latest_boost = influencer.boosts.latest('boost_datetime')
        boost_value = latest_boost.boost_value
        boost_datetime = latest_boost.boost_datetime
    except:
        boost_value = None
        boost_datetime = None

    influencer_doc = InfluencerDoc.get_influencer(influencer.userprofile.user_id)
    influencer_doc.boost_value = boost_value
    influencer_doc.boost_datetime = boost_datetime
    influencer_doc.save()
