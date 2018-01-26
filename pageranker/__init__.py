import numpy as np
import scipy.sparse.linalg as sla
from elasticsearch import Elasticsearch

import settings


def pagerank(es_connection=settings.ELASTIC_CONNECTION, alpha=0.2):
    es = Elasticsearch([es_connection])
    res = es.search(index=settings.INDEX_NAME, body={"query": {"match_all": {}}}, size=10000)
    urls = {}
    urls_T = list()
    i = 0
    for hit in res['hits']['hits']:
        link = hit['_source']['blog']['url']
        if link[-1] == '/':
            link = link[:-1]
        urls[link] = i
        urls_T.append(link)
        i += 1
    graph_t = list()
    n = len(urls)
    i = 0
    for hit in res['hits']['hits']:
        graph_t.append(list())
        for post in hit['_source']['blog']['posts']:
            for comment in post['post_comments']:
                link = comment['comment_url']
                if link[-1] == '/':
                    link = link[:-1]
                if link in urls:
                    graph_t[i].append(urls[link])
        i += 1

    graph = []
    for i in range(0, n):
        graph.append([])
        for j in range(0, n):
            if i in graph_t[j]:
                graph[i].append(j)

    matrix_temp = []
    for i in range(0, n):
        temp = []
        if len(graph[i]) == 0:
            for j in range(0, n):
                temp.append(1 / n)
        else:
            for j in range(0, n):
                if j in graph[i]:
                    temp.append(alpha / n + (1 - alpha) / len(graph[i]))
                else:
                    temp.append(alpha / n)

        matrix_temp.append(temp)

    for row in matrix_temp:
        sum = 0
        for i in row:
            sum += i
        row[n-1] -= sum-1

    matrix = np.array(matrix_temp)
    eval, evec = sla.eigs(matrix.T, k=1, which='LM')

    sum = 0
    for i in range(0, n):
        sum += evec[i][0].real

    scaled = list()
    for i in range(0, n):
        scaled.append(evec[i][0].real / sum)

    # for i in range(0, n):  # Uncomment to see pageranks
    #     print(urls_T[i])
    #     print(scaled[i])

    for hit in res['hits']['hits']:
        doc = es.get(index=settings.INDEX_NAME, doc_type='doc', id=hit['_id'])['_source']
        link = hit['_source']['blog']['url']
        if link[-1] == '/':
            link = link[0:len(link)-1]
        doc['blog']['pagerank'] = scaled[urls[link]]
        es.index(index=settings.INDEX_NAME, doc_type='doc', id=hit["_id"], body=doc)
