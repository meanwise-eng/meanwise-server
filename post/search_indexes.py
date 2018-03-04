from django.utils import timezone
from django.db.models import Q
from haystack import indexes
from post.models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=False)
    post_text = indexes.CharField(model_attr="text", null=True)
    post_id = indexes.CharField(model_attr="id")
    created_on = indexes.DateTimeField(model_attr='created_on')
    tag_names = indexes.MultiValueField()
    topic_texts = indexes.MultiValueField()

    # autocomplete = indexes.EdgeNgramField()

    # @staticmethod
    # def prepare_autocomplete(obj):
    #    return " ".join((
    #        obj.address, obj.city, obj.zip_code
    #    ))

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects\
            .filter(created_on__lte=timezone.now())\
            .filter(is_deleted=False) \
            .filter(Q(story__isnull=True) | Q(story_index=1))

    def prepare_text(self, obj):
        if (obj.story):
            return ' '.join([post.text.lower() for post in obj.story.posts.filter(is_deleted=False)])
        else:
            return obj.text.lower()

    def prepare_term(self, obj):
        return self.prepare_text(obj)


    def prepare_topic_texts(self, obj):
        if (obj.story):
            return list(set([topic.text.lower() for p in obj.story.posts.filter(is_deleted=False) for topic in p.topics.all()]))
        else:
            return [topic.text.lower() for topic in obj.topics.all()]

    def prepare_tag_names(self, obj):
        if obj.story:
            return [tag.name.lower() for p in obj.story.posts.filter(is_deleted=False) for tag in p.tags.all()]
        else:
            return [tag.name.lower() for tag in obj.tags.all()]
