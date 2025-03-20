from elasticsearch import Elasticsearch
import os
# def get_elasticsearch_client():
#     es = Elasticsearch(
#         [
#             {'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'},
#             {'host': 'elasticsearch', 'port': 9201, 'scheme': 'http'},
#         ],
#         retry_on_timeout=True,
#         max_retries=3,
#         timeout=30
#     )
#     return es


# def get_elasticsearch_client():
#     es = Elasticsearch([
#         {'host': '10.96.80.76', 'port': 9200, 'scheme': 'http'},
#         {'host': '10.96.80.76', 'port': 9201, 'scheme': 'http'}
#     ],
#         basic_auth=('elastic', 'password'),
#         retry_on_timeout=True,
#         max_retries=3,
#         timeout=30        
#     )
#     return es

def get_elasticsearch_client():
    elasticsearch_url = os.environ.get('ELASTICSEARCH_URL')
    if elasticsearch_url:
        urls = elasticsearch_url.split(',')
        es = Elasticsearch(urls,
            basic_auth=('elastic', 'password'),
            retry_on_timeout=True,
            max_retries=3,
            timeout=30        
        )
        return es
    else:
        print("ELASTICSEARCH_URL environment variable is not set.")
        return None