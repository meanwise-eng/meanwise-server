from django.utils import timezone
from haystack import indexes
from userprofile.models import UserProfile

class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=False)
    id = indexes.CharField(model_attr="id")
    first_name = indexes.CharField(model_attr="first_name")
    last_name = indexes.CharField(model_attr="last_name")
    username = indexes.CharField(model_attr='username')
    #skill_name = indexes.CharField()
    #autocomplete = indexes.EdgeNgramField()

    #@staticmethod
    #def prepare_autocomplete(obj):
    #    return " ".join((
    #        obj.address, obj.city, obj.zip_code
    #    ))

    def get_model(self):
        return UserProfile

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            created_on__lte=timezone.now()
        )

