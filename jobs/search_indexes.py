from haystack import indexes
from haystack.query import SQ

from .models import Job


class JobIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='title')
    company = indexes.CharField()
    role = indexes.CharField(model_attr='role')
    kind = indexes.CharField(model_attr='kind')
    skills = indexes.MultiValueField(null=True)
    content_auto = indexes.EdgeNgramField(model_attr='title')

    def get_model(self):
        return Job

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare_skills(self, obj):
        return [skill.text.lower() for skill in obj.skills.all()]

    def prepare_company(self, obj):
        return obj.company.company_name

    def index_by_skill(self, *args):
        search_queries = [title for title in args]
