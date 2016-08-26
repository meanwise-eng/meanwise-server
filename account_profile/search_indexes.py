from django.db.models import Q

from haystack import indexes

from .models import Profile, Skill, Profession, Language

class ProfileIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text        = indexes.CharField(document=True, use_template=True)
    skills      = indexes.CharField()
    interests   = indexes.CharField()
    content_auto= indexes.NgramField()

    class Meta:
        model   = Profile
        fields  = ('text', 'id', 'skills', 'interests', 'content_auto')

    def get_updated_field(self):
        return 'last_updated'

    def index_queryset(self, using=None):
        query = Q(username='') | Q(username__istartswith='sq_test_')
        return self.get_model().objects.exclude(query)

    def prepare_skills(self, obj):
        return [s.text for s in obj.skills.all()]

    def prepare_interests(self, obj):
        return [i.name for i in obj.interests.all()]

    def prepare_content_auto(self, obj):
        content  = '%s %s %s %s' % (obj.username, obj.first_name, obj.middle_name, obj.last_name)
        content += '%s %s' % (obj.message, obj.description)
        content += ' '.join(self.prepare_skills(obj))
        content += ' '.join(self.prepare_interests(obj))
        return content


class SkillIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text        = indexes.CharField(document=True, model_attr='text')
    content_auto= indexes.NgramField()

    class Meta:
        model   = Skill
        fields  = ('id', 'text', )

    def get_updated_field(self):
        return 'last_updated'

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(searchable=True)

    def prepare_content_auto(self, obj):
        return obj.text

    def load_all_queryset(self):
        """ Returns all related objects to particular skill."""


class ProfessionIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text        = indexes.CharField(document=True)
    content_auto= indexes.NgramField()

    class Meta:
        model   = Profession
        fields  = ('id', 'text', )

    def get_updated_field(self):
        return 'last_updated'

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(searchable=True)

    def prepare_content_auto(self, obj):
        return obj.text

class LanguageIndex(indexes.ModelSearchIndex, indexes.Indexable):
    text        = indexes.CharField(document=True)
    content_auto= indexes.NgramField()

    class Meta:
        model   = Language
        fields  = ('id', 'text', )

    def get_updated_field(self):
        return 'last_updated'

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(searchable=True)

    def prepare_content_auto(self, obj):
        return obj.text
