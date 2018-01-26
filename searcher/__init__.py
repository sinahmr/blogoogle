from elasticsearch import Elasticsearch

import settings


def search(es_connection=settings.ELASTIC_CONNECTION):
    es = Elasticsearch([es_connection])

    again = 'y'
    while again.lower().startswith('y'):
        query = {
            "query": {
                "bool": {
                    "should": []
                }
            }
        }

        title_query = input("Title Query: ")
        if title_query:
            title_weight = float(input("Title Weight: "))
            query["query"]["bool"]["should"].append({
                "match": {
                    "blog.title": {
                        "query": title_query,
                        "boost": title_weight
                    }
                }
            })

        post_title_query = input("Post Title Query: ")
        if post_title_query:
            post_title_weight = float(input("Post Title Weight: "))
            query["query"]["bool"]["should"].append({
                "match": {
                    "blog.posts.post_title": {
                        "query": post_title_query,
                        "boost": post_title_weight
                    }
                }
            })

        content_query = input("Content Query: ")
        if content_query:
            content_weight = float(input("Content Weight: "))
            query["query"]["bool"]["should"].append({
                "match": {
                    "blog.posts.post_content": {
                        "query": content_query,
                        "boost": content_weight
                    }
                }
            })

        use_pagerank = input("Use PageRank? (y / n) ")
        if use_pagerank.lower().startswith('y'):
            final_query = {
                'query': {
                    'function_score': {
                        'query': query['query'],
                        'script_score': {
                            'script': {
                                'source': "doc['blog.pagerank'].value*_score"
                            }
                        }
                    }
                }
            }
            # query['function_score'] = {'field_value_factor':{'field':"pagerank", 'missing':1}}
        else:
            final_query = query

        size = int(input("Result Count? (default to 10) ") or 10)
        res = es.search(index=settings.INDEX_NAME, body=final_query, size=size)

        i = 0
        for hit in res['hits']['hits']:
            i += 1
            print()
            print("Result " + str(i) + ":")
            print("ID: " + hit["_id"])
            print("URL: " + hit["_source"]["blog"]["url"])
            print("Title: " + hit["_source"]["blog"]["title"])

            for idx, post in enumerate(hit["_source"]["blog"]["posts"]):
                print()
                print("Post Title %d: " % (idx + 1) + post["post_title"])
                print("Post Content %d: " % (idx + 1) + post["post_content"])

            print("\n----------------------------------------------------")

        again = input("Search Again? (y / n) ")
