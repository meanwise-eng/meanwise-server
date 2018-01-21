from django.utils import timezone
from haystack import indexes
from userprofile.models import UserProfile, Profession, Skill
from post.models import Post


class UserProfileIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=False)
    userprofile_id = indexes.CharField(model_attr="id")
    first_name = indexes.CharField(model_attr="first_name")
    last_name = indexes.CharField(model_attr="last_name")
    username = indexes.EdgeNgramField()
    skills_text = indexes.NgramField()
    created_on = indexes.DateTimeField(model_attr='created_on')
    featured = indexes.BooleanField()

    term = indexes.NgramField()
    # autocomplete = indexes.EdgeNgramField()

    # @staticmethod
    # def prepare_autocomplete(obj):
    #    return " ".join((
    #        obj.address, obj.city, obj.zip_code
    #    ))

    def get_model(self):
        return UserProfile

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            created_on__lte=timezone.now()
        )

    def prepare_username(self, obj):
        return ' '.join([obj.user.username, obj.first_name, obj.last_name])

    def prepare_skills_text(self, obj):
        return ' '.join([skill.lower() for skill in obj.skills_list])

    def prepare_term(self, obj):
        value = obj.user.username.lower()
        value += ' ' + ' '.join([skill.lower() for skill in obj.skills_list])
        value += ' %s %s %s' % (obj.first_name or '',
                                obj.last_name or '', obj.city or '')

        return value

    def prepare_featured(self, obj):
        return True


class ProfessionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        model_attr='text', document=True, use_template=False)
    profession_id = indexes.IntegerField(model_attr='id')

    autocomplete = indexes.EdgeNgramField(model_attr='text')

    def get_model(self):
        return Profession


class SkillIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        model_attr='text', document=True, use_template=False)
    skill_id = indexes.IntegerField(model_attr='id')

    autocomplete = indexes.EdgeNgramField(model_attr='text')

    image_url = indexes.CharField()

    def get_model(self):
        return Skill

    def prepare_image_url(self, obj):
        posts = Post.objects.filter(topics__text=obj.text).order_by('-created_on')

        for post in posts:
            if post.post_thumbnail() is not None:
                return post.post_thumbnail().url

        return None
