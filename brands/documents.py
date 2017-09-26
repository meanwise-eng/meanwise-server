from django_elasticsearch_dsl import DocType, Index, fields

from .models import Brand

from boost.models import Boost

brands = Index('mw_brands')

brands.settings(
    number_of_shards=1,
    number_of_replicas=0
)


class BrandDocument(DocType):

    boost_value = fields.IntegerField()
    boost_datetime = fields.DateField()

    class Meta:
        model = Brand

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
