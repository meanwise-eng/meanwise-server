from django.conf import settings

from requests_aws_sign import AWSV4Sign
from boto3 import session

from haystack.backends.elasticsearch2_backend import (Elasticsearch2SearchBackend,
                                                      Elasticsearch2SearchEngine)


class MeanwiseElasticSearchBackend(Elasticsearch2SearchBackend):

    auth = ''

    def __init__(self, connection_alias, **connection_options):

        # if 'http_auth' not in connection_options:
        # 	if self.auth:
        # 		session = session.Session()
        # 		credentials = session.get_credentials()
        # 		region = session.region_name or settings.AWS_S3_REGION_NAME

        # 		service = 'es'
        # 		es_host = settings.HAYSTACK_ES_URL
        # 		self.auth = AWSV4Sign(credentials, region, service)

                    #connection_options['KWARGS']['http_auth'] = self.auth

        super().__init__(connection_alias, **connection_options)

        MY_SETTINGS = {
            'settings': {
                'index': {
                    'analysis': {
                        'analyzer': {
                            'ngram_analyzer': {
                                'type': 'custom',
                                'tokenizer': 'lowercase',
                                        'filter': ['haystack_ngram']
                            },
                            'edgengram_analyzer': {
                                'type': 'custom',
                                'tokenizer': 'lowercase',
                                'filter': ['haystack_edgengram']
                            }
                        },
                        'tokenizer': {
                            'haystack_ngram_tokenizer': {
                                'type': 'nGram',
                                'min_gram': 3,
                                'max_gram': 3
                            },
                            'haystack_edgengram_tokenizer': {
                                'type': 'edgeNGram',
                                'min_gram': 3,
                                'max_gram': 15,
                                'side': 'front'
                            }
                        },
                        'filter': {
                            'haystack_ngram': {
                                'type': 'nGram',
                                'min_gram': 3,
                                'max_gram': 3
                            },
                            'haystack_edgengram': {
                                'type': 'edgeNGram',
                                'min_gram': 3,
                                'max_gram': 15
                            }
                        }
                    }
                }
            }
        }

        setattr(self, 'DEFAULT_SETTINGS', MY_SETTINGS)


class MeanwiseElasticSearchEngine(Elasticsearch2SearchEngine):
    backend = MeanwiseElasticSearchBackend
