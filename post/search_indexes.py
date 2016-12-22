from django.utils import timezone
from haystack import indexes
from post.models import Post

class PostIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    #post_text = indexes.CharField(model_attr="text")

    autocomplete = indexes.EdgeNgramField()

    #@staticmethod
    #def prepare_autocomplete(obj):
    #    return " ".join((
    #        obj.address, obj.city, obj.zip_code
    #    ))

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            created__lte=timezone.now()
        )

