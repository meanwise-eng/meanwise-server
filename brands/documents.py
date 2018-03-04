from django_elasticsearch_dsl import DocType, Index, fields
from django.urls import reverse

from common.api_helper import build_absolute_uri

from .models import Brand

from boost.models import Boost

brands = Index('mw_brands')

brands.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@brands.doc_type
class BrandDocument(DocType):

    logo = fields.StringField(index='not_analyzed')
    logo_thumbnail = fields.StringField(index='not_analyzed')
    profile_image = fields.StringField(index='not_analyzed')
    compact_display_image = fields.StringField(index='not_analyzed')

    type = fields.StringField(index='not_analyzed')
    url = fields.StringField(inidex='not_analyzed')

    boost_value = fields.IntegerField()
    boost_datetime = fields.DateField()

    members = fields.StringField(index='not_analyzed')
    posts = fields.StringField(index='not_analyzed')

    description = fields.StringField(index='not_analyzed')

    interest_ids = fields.IntegerField(index='not_analyzed')

    class Meta:
        model = Brand
        fields = ('name', 'profile_color', 'created_on', 'last_update_on')

    def prepare_logo(self, obj):
        return obj.logo.url

    def prepare_logo_thumbnail(self, obj):
        return obj.logo_thumbnail.url

    def prepare_profile_image(self, obj):
        if not obj.profile_image:
            return None

        return obj.profile_image.url

    def prepare_compact_display_image(self, obj):
        return obj.compact_display_image.url

    def prepare_boost_value(self, obj):
        try:
            boost = obj.boosts.latest('boost_datetime')
        except Boost.DoesNotExist:
            return None
        return boost.boost_value

    def prepare_boost_datetime(self, obj):
        try:
            boost = obj.boosts.latest('boost_datetime')
        except Boost.DoesNotExist:
            return None
        return boost.boost_datetime

    def prepare_members(self, obj):
        return build_absolute_uri(reverse('brand-members', kwargs={'brand_id': obj.id}))

    def prepare_posts(self, obj):
        return build_absolute_uri(reverse('brand-posts', kwargs={'brand_id': obj.id}))

    def prepare_interest_ids(self, obj):
        return [p.interest.id for p in obj.posts.all()]
