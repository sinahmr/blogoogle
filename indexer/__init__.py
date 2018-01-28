import json
import os

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

import settings


def delete_index(es_connection=settings.ELASTIC_CONNECTION):
    es = Elasticsearch([es_connection])
    es.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])


def index(directory='result', es_connection=settings.ELASTIC_CONNECTION):
    es = Elasticsearch([es_connection])
    if not es.indices.exists(index=settings.INDEX_NAME):
        es.indices.create(index=settings.INDEX_NAME, body=settings.ELASTIC_INDEX_CONFIG)
    count = len(os.listdir('%s' % directory))
    for file_num in range(count):
        if file_num % 50 == 0:
            print('%.2f%%' % (100 * file_num / count))
        with open('%s/%d.json' % (directory, file_num), 'r', encoding='utf-8') as file:
            obj = json.loads(file.read())
            try:
                blog_id = obj['blog_url'].split('.blog.ir')[0].split('/')[-1]
                if obj['type'] == 'blog':
                    doc = {
                        'blog': {
                            'url': obj['blog_url'],
                            'title': obj['blog_name'],
                            'posts': [],
                            'pagerank': 0
                        }
                    }

                    # Creating posts
                    for i in range(1, 5 + 1):
                        try:
                            post_title = obj['post_title_%s' % i]
                            post = {
                                'post_url': obj['post_url_%s' % i],
                                'post_title': post_title,
                                'post_content': obj['post_content_%s' % i],
                                'post_comments': [],
                            }
                            doc['blog']['posts'].append(post)
                        except KeyError:  # Blogs may have less than 5 posts
                            pass

                    es.index(index=settings.INDEX_NAME, doc_type='doc', id=blog_id, body=doc)
                else:
                    try:
                        doc = es.get(index=settings.INDEX_NAME, doc_type='doc', id=blog_id)['_source']
                        for post in doc['blog']['posts']:
                            if post['post_url'] == obj['post_url']:
                                for url in obj['comment_urls']:
                                    post['post_comments'].append({
                                        'comment_url': url
                                    })
                                if 'post_full_content' in obj:
                                    post['post_full_content'] = obj['post_full_content']
                        es.index(index=settings.INDEX_NAME, doc_type='doc', id=blog_id, body=doc)
                    except NotFoundError:
                        pass
            except Exception:
                print('Bad data: %d.json' % file_num)
