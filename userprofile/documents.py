import datetime
import elasticsearch
from django_elasticsearch_dsl import Integer, String, Date
from elasticsearch_dsl import analyzer, tokenizer, Index, DocType

influencers = Index('mw_influencers')
influencers.settings(
    number_of_shards=1,
    number_of_replicas=0
)

comma_tokenizer = tokenizer(
    'comma_tokenizer',
    type='pattern',
    pattern=','
)
comma_analyzer = analyzer(
    'comma_analyzer',
    tokenizer=comma_tokenizer,
)

influencers.analyzer(comma_analyzer)


@influencers.doc_type
class Influencer(DocType):
    user_id = Integer()
    topics_weekly = String(index='not_analyzed')
    topics_overall = String(index='not_analyzed')
    popularity_weekly = Integer()
    popularity_overall = Integer()
    friends = Integer()
    last_reset = Date()

    boost_value = Integer()
    boost_datetime = Date()

    class Meta:
        index = 'mw_influencers'

    @classmethod
    def get_influencer(cls, user_id):
        now = datetime.datetime.now()
        try:
            influencer = Influencer.get(id=user_id)
        except elasticsearch.NotFoundError:
            influencer = Influencer()
            influencer.meta.id = user_id
            influencer.topics_weekly = []
            influencer.topics_overall = []
            influencer.popularity_weekly = 0
            influencer.popularity_overall = 0
            influencer.friends = 0
            influencer.last_reset = now
            influencer.boost_value = None
            influencer.boost_datetime = None

        if influencer.last_reset < (now - datetime.timedelta(weeks=1)):
            influencer.topics_overall = influencer.topics_overall + influencer.topics_weekly
            influencer.popularity_overall = influencer.popularity_overall \
                + influencer.popularity_weekly
            influencer.topics_weekly = []
            influencer.popularity_weekly = 0
            influencer.last_reset = now

        return influencer
