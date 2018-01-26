ELASTIC_CONNECTION = {
    'host': 'localhost',
    'port': 9200,
}

ELASTIC_INDEX_CONFIG = {
    'settings': {
        'index': {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'blocks': {
                'read_only': False,
                'read_only_allow_delete': None
            }
        }
    }
}
INDEX_NAME = 'blog_index'
