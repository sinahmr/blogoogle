import json
import os

from elasticsearch import Elasticsearch

import settings


def delete_index(es_connection=settings.ELASTIC_CONNECTION):
    es = Elasticsearch([es_connection])
    es.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])


def index(directory='content', es_connection=settings.ELASTIC_CONNECTION):
    es = Elasticsearch([es_connection])
    if not es.indices.exists(index=settings.INDEX_NAME):
        es.indices.create(index=settings.INDEX_NAME, body=settings.ELASTIC_INDEX_CONFIG)
    for blog_file_name in os.listdir('%s/blog' % directory):
        with open('%s/blog/%s' % (directory, blog_file_name), 'r', encoding='utf-8') as blog_file:
            blog = json.loads(blog_file.read())
            doc = {
                'blog': {
                    'url': blog['blog_url'],
                    'title': blog['blog_name'],
                    'posts': []
                }
            }
            blog_name = blog_file_name[:-5]

            # Creating posts
            for i in range(1, 5+1):
                try:
                    post_title = blog['post_title_%s' % i]
                    post = {
                        'post_url': blog['post_url_%s' % i],
                        'post_title': post_title,
                        'post_content': blog['post_content_%s' % i],
                        'post_comments': [],
                    }

                    # Fetching comment urls
                    comment_urls = list()
                    post_file_name = '%s (%d).json' % (blog_name, i)
                    with open('%s/post/%s' % (directory, post_file_name), 'r', encoding='utf-8') as post_file:
                        loaded_post = json.loads(post_file.read())
                        post['post_full_content'] = loaded_post['post_full_content']
                        for comment_url in loaded_post['comment_urls']:
                            if comment_url not in comment_urls:
                                comment_urls.append(comment_url)
                    for comment_url in comment_urls:
                        post['post_comments'].append({
                            'comment_url': comment_url
                        })
                    doc['blog']['posts'].append(post)
                except KeyError:
                    pass
            es.index(index=settings.INDEX_NAME, doc_type='doc', id=blog_name, body=doc)
