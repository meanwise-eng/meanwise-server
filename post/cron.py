import time
import logging
from post.models import TrendingTopicsInterest, Post
from userprofile.models import Interest

def my_scheduled_job():
    start_time = time.time()
    #delete old values
    for tt in TrendingTopicsInterest.objects.all():
        tt.delete()
    for interest in Interest.objects.all():
        topics_rank = {}
        #fetch all posts for given interests
        posts = Post.objects.filter(interest=interest).filter(is_deleted=False)
        #calculate topic rank value for last one week, based on num of likes and num of comments
        for post in posts:
            post_rank_value = post.rank_post_value()
            post_topics = post.topics.all()
            for post_topic in post_topics:
                if post_topic.text in topics_rank:
                    topics_rank[post_topic.text] += post_rank_value
                else:
                    topics_rank[post_topic.text] = post_rank_value
        #sort the topics based on rank value
        topics = sorted(topics_rank, key=topics_rank.get, reverse=True)[:10]
        TrendingTopicsInterest.objects.create(interest=interest, topics=topics)

    t = int((time.time() - start_time) * 1000)

    extra = {
        'time': t,
        'tags': ['trending-topics']
    }
    logger = logging.getLogger('meanwise_backend.%s' % __name__)
    adapter = logging.LoggerAdapter(logger, extra)
    adapter.info("Calculated trending topics.")
