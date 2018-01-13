import json
import os

from elasticsearch import Elasticsearch

import settings

es = Elasticsearch([settings.ELASTIC_CONNECTION])


def delete_index():
    es.indices.delete(index=settings.INDEX_NAME, ignore=[400, 404])


def index():
    if not es.indices.exists(index=settings.INDEX_NAME):
        es.indices.create(index=settings.INDEX_NAME)
    for blog_file_name in os.listdir('content/blog'):
        with open('content/blog/%s' % blog_file_name, 'r') as blog_file:
            blog = json.load(blog_file)
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
                    comment_urls = set()
                    for post_file_name in os.listdir('content/post'):
                        if post_file_name.startswith(blog_name):
                            with open('content/post/%s' % post_file_name, 'r') as post_file:
                                for comment_url in json.load(post_file)['comment_urls']:
                                    comment_urls.add(comment_url)
                    for comment_url in comment_urls:
                        post['post_comments'].append({
                            'comment_url': comment_url
                        })
                    doc['blog']['posts'].append(post)
                except KeyError:
                    pass
            es.index(index=settings.INDEX_NAME, doc_type='doc', id=blog_name, body=doc)
