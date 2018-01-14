import logging
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

import elasticsearch

from django.urls import reverse
from common.api_helper import build_absolute_uri

from boost.models import Boost

from .models import Brand
from post.documents import ExploreOrgDocument

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@receiver(post_save, sender=Brand, dispatch_uid='brand.saved')
def create_org_document(sender, **kwargs):
    brand = kwargs['instance']

#    if kwargs['created'] == False:
#        return

    org = ExploreOrgDocument(_id=brand.id, name=brand.name, description=brand.description,
                      type='brand', compact_display_image=brand.compact_display_image.url,
                      created_on=brand.created_on,
                      url=build_absolute_uri(reverse('brand-details', args=[brand.id])))
    org.skills = []
    org.save()


@receiver(post_delete, sender=Brand, dispatch_uid='brand.deleted')
def delete_org_document(sender, **kwargs):
    brand = kwargs['instance']

    org = ExploreOrgDocument.get(id=brand.id)
    org.delete()
