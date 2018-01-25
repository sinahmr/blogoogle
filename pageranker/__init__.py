import numpy as np
import scipy.sparse.linalg as sla

from elasticsearch import Elasticsearch

import settings


def pagerank(es_connection=settings.ELASTIC_CONNECTION):
    es = Elasticsearch([es_connection])
    #res = es.get(index=settings.INDEX_NAME, doc_type='doc', id='shayanh')
    #print(res['_source']['blog']['posts'][0]['post_comments'])
    res = es.search(index=settings.INDEX_NAME, body={"query": {"match_all": {}}}, size = 1000)
    urls = {}
    urls_T = list()
    i = 0
    for hit in res['hits']['hits']:
        link = hit['_source']['blog']['url']
        if link[-1] == '/':
            link = link[0:len(link)-1]
        #print(link)
        urls[link] = i
        urls_T.append(link)
        #print(link + " " + str(i))
        i = i+1
    #print(urls)
    graph_t = list()
    n = len(urls)
    i = 0
    for hit in res['hits']['hits']:
        graph_t.append(list())
        for post in hit['_source']['blog']['posts']:
            #print(comment)
            #print(comment['post_url'])
            for comment in post['post_comments']:
                link = comment['comment_url']
                if link[-1] == '/':
                    link = link[0:len(link) - 1]
                if link in urls: # it's possible to reference external blogs right?!
                    graph_t[i].append(urls[link])

        i = i+1

    graph = []

    for i in range(0, n):
        graph.append([])
        for j in range(0, n):
            if i in graph_t[j]:
                graph[i].append(j)

    #print(graph)

    alpha = 0.2

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

    #print(n)
    #print(len(urls_T))
    for row in matrix_temp:
        #print(row)
        sum = 0
        for i in row:
            sum += i
        #print(sum)
        row[n-1] -= sum-1


    matrix = np.array(matrix_temp)

    eval, evec = sla.eigs(matrix.T, k=1, which='LM')

    #print(eval)

    sum = 0
    for i in range(0, n):
        sum += evec[i][0].real

    scaled = list()

    #newsum = 0
    for i in range(0, n):
        scaled.append(evec[i][0].real / sum)
        #newsum += scaled[i]

    #print(newsum)

    for i in range(0,n):
        print(urls_T[i])
        print(scaled[i])
    #print(evec)

    #for row in np.dot(np.array(scaled).T, matrix).T:
    #print(row)

    for hit in res['hits']['hits']:
        doc = es.get(index=settings.INDEX_NAME, doc_type='doc', id=hit['_id'])['_source']
        link = hit['_source']['blog']['url']
        if link[-1] == '/':
            link = link[0:len(link)-1]
        doc['blog']['pagerank'] = scaled[urls[link]]
        es.index(index=settings.INDEX_NAME, doc_type='doc', id=hit["_id"], body=doc)

