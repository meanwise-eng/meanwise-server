from django.utils import timezone
from haystack import indexes
from post.models import Post

class PostIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=False)
    post_text = indexes.CharField(model_attr="text", null=True)
    post_id = indexes.CharField(model_attr="id")
    interest_name = indexes.CharField()
    created_on = indexes.DateTimeField(model_attr='created_on')
    #interest = 

    #autocomplete = indexes.EdgeNgramField()

    #@staticmethod
    #def prepare_autocomplete(obj):
    #    return " ".join((
    #        obj.address, obj.city, obj.zip_code
    #    ))

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            created_on__lte=timezone.now()
        ).select_related('interest')

    def prepare_interest_name(self, obj):
        return obj.interest.name

