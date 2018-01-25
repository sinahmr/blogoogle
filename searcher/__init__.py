from elasticsearch import Elasticsearch

import settings


def search(es_connection=settings.ELASTIC_CONNECTION):
    es = Elasticsearch([es_connection])

    again = 'y'

    while again == 'y':
        query = {"query": {"bool": {"should": []}}}
        titleQuery = input("Title Query:\n")
        if(len(titleQuery) > 0):
            titleWeight = input("Title Weight:\n")
            query["query"]["bool"]["should"].append({"match":{"blog.title":{"query": titleQuery,"boost": titleWeight}}})
        postTitleQuery = input("Post Title Query:\n")
        if(len(postTitleQuery) > 0):
            postTitleWeight = input("Post Title Weight:\n")
            query["query"]["bool"]["should"].append({"match": {"blog.posts.post_title": {"query": postTitleQuery, "boost": postTitleWeight}}})
        contentQuery = input("Content Query:\n")
        if(len(contentQuery) > 0):
            contentWeight = input("Content Weight:\n")
            query["query"]["bool"]["should"].append({"match": {"blog.posts.post_content": {"query": contentQuery, "boost": contentWeight}}})


        usePagerank = input("Use PageRank?\n")
        if usePagerank == 'y':
            finalQuery = {'query':{'function_score': {'query': query['query'],
                'script_score': {'script': {'source': "doc['blog.pagerank'].value*_score"}}}}}
            #query['function_score'] = {'field_value_factor':{'field':"pagerank", 'missing':1}}
        else:
            finalQuery = query

        size = input("Result Count:\n")
        if len(size) == 0:
            size = 10

        res = es.search(index=settings.INDEX_NAME, body=finalQuery, size=size)

        i = 0
        for hit in res['hits']['hits']:
            i += 1
            print("Result " + str(i) + ":")
            print("ID: " + hit["_id"])
            print("URL: " + hit["_source"]["blog"]["url"])
            print("Title: " + hit["_source"]["blog"]["title"])

            for post in hit["_source"]["blog"]["posts"]:
                print("............")
                print("Post Title: " + post["post_title"])
                print("Post Content: " + post["post_content"])

            print("----------------------------------------------------")
            #print(hit["_source"]["blog"]["pagerank"])

        again = input("Search Again?\n")