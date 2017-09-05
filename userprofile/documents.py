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
    interests_weekly = String(analyzer=comma_analyzer)
    interests_overall = String(analyzer=comma_analyzer)
    popularity_weekly = Integer()
    popularity_overall = Integer()
    friends = Integer()
    last_reset = Date()

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
            influencer.interests_weekly = ''
            influencer.interests_overall = ''
            influencer.popularity_weekly = 0
            influencer.popularity_overall = 0
            influencer.friends = 0
            influencer.last_reset = now

        if influencer.last_reset < (now - datetime.timedelta(weeks=1)):
            influencer.interests_overall = '%s,%s' % (
                influencer.interests_overall, influencer.interests_weekly)
            influencer.popularity_overall = influencer.popularity_overall \
                + influencer.popularity_weekly
            influencer.interests_weekly = ''
            influencer.popularity_weekly = 0
            influencer.last_reset = now

        return influencer
