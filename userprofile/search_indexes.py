from django.utils import timezone
from haystack import indexes
from userprofile.models import UserProfile, Profession, Skill

class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=False)
    userprofile_id = indexes.CharField(model_attr="id")
    first_name = indexes.CharField(model_attr="first_name")
    last_name = indexes.CharField(model_attr="last_name")
    username = indexes.CharField(model_attr='username')
    skills_text = indexes.MultiValueField()
    created_on = indexes.DateTimeField(model_attr='created_on')
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

    def prepare_skills_text(self, obj):
        return  [skill.text for skill in obj.skills.all()] 

class ProfessionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='text', document=True, use_template=False)
    profession_id = indexes.IntegerField(model_attr='id')

    autocomplete = indexes.EdgeNgramField(model_attr='text')

    def get_model(self):
        return Profession

class SkillIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='text', document=True, use_template=False)
    skill_id = indexes.IntegerField(model_attr='id')

    autocomplete = indexes.EdgeNgramField(model_attr='text')

    def get_model(self):
        return Skill
