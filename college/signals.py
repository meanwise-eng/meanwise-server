import logging
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

import elasticsearch

from django.urls import reverse
from common.api_helper import build_absolute_uri

from boost.models import Boost

from .models import College
from post.documents import ExploreOrgDocument

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@receiver(post_save, sender=College, dispatch_uid='college.saved')
def create_org_document(sender, **kwargs):
    college = kwargs['instance']

#    if kwargs['created'] == False:
#        return

    org = ExploreOrgDocument(_id=college.id, name=college.name, description=college.description,
                      type='college', compact_display_image=college.compact_display_image.url,
                      created_on=college.created_on,
                      url=build_absolute_uri(reverse('college-details', args=[college.id])))
    org.skills = []
    org.save()


@receiver(post_delete, sender=College, dispatch_uid='college.deleted')
def delete_org_document(sender, **kwargs):
    college = kwargs['instance']

    org = ExploreOrgDocument.get(id=college.id)
    org.delete()
