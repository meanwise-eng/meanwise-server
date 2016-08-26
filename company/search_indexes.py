from haystack import indexes

from .models import Company


class CompanyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    company_name = indexes.CharField()
    content_auto = indexes.EdgeNgramField(model_attr='company_name')

    def get_model(self):
        return Company

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
