from elasticsearch import Elasticsearch

import settings


def search(es_connection=settings.ELASTIC_CONNECTION):
    es = Elasticsearch([es_connection])

    query = {"query": {"bool": {"should": []}}}

    titleQuery = input("Title Query:")
    if(len(titleQuery) > 0):
        titleWeight = input("Title Weight:")
        query["query"]["bool"]["should"].append({"match":{"blog.title":{"query": titleQuery,"boost": titleWeight}}})
    postTitleQuery = input("Post Title Query:")
    if(len(postTitleQuery) > 0):
        postTitleWeight = input("Post Title Weight:")
        query["query"]["bool"]["should"].append({"match": {"blog.posts.post_title": {"query": postTitleQuery, "boost": postTitleWeight}}})
    contentQuery = input("Content Query:")
    if(len(contentQuery) > 0):
        contentWeight = input("Content Weight:")
        query["query"]["bool"]["should"].append({"match": {"blog.posts.post_content": {"query": contentQuery, "boost": contentWeight}}})


    usePagerank = input("Use PageRank?")
    if usePagerank == 'y':
        finalQuery = {'query':{'function_score': {'query': query['query'],
            'script_score': {'script': {'source': "doc['pagerank'].value"}}}}}
    else:
        finalQuery = query

    res = es.search(index=settings.INDEX_NAME, body=finalQuery, size=1000)

    for hit in res['hits']['hits']:
        print(hit["_source"]["blog"]["url"])
        print(hit["_source"]["pagerank"])