from elasticsearch import Elasticsearch

def get_elasticsearch_client():
    es = Elasticsearch(
        [
            {'host': 'elasticsearch', 'port': 9200, 'scheme': 'http'},
            {'host': 'elasticsearch', 'port': 9201, 'scheme': 'http'},
        ],
        retry_on_timeout=True,
        max_retries=3,
        timeout=30
    )
    return es
