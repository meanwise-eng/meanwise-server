from haystack import indexes

from .models import CourseMajor


class CourseMajorIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    content_auto = indexes.NgramField()

    class Meta:
        model = CourseMajor
        fields = ('id', 'text', )

    def get_updated_field(self):
        return 'last_updated'

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(searchable=True)

    def prepare_content_auto(self, obj):
        return obj.text
