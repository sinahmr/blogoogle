from subprocess import call

# import crawler
import indexer
import pageranker
import searcher


# start_urls = [
#     'http://shayanh.blog.ir/',
#     'http://avocado.blog.ir/',
#     'http://sirnarenji.blog.ir/',
#     'http://arameeesh.blog.ir/'
# ]
# start_urls = ','.join(start_urls)

def ui_crawler():
    print('Crawler')
    start_urls = input('Start URLs? (comma separated) ').replace(' ', '')
    in_degree = input('in_degree? (default to 5) ')
    n = input('n? (default to 1000) ')
    command = 'scrapy crawl blogs -a start_urls=%s' % start_urls
    if in_degree:
        command += ' -a in_degree=%s' % in_degree
    if n:
        command += ' -a n=%s' % n
    # We run crawler like the line below because calling crawler API wouldn't load settings
    call(command, shell=True, cwd='crawler')
    # crawler.run(start_urls, in_degree, n)  # For debugging purposes TODO delete


def ui_indexer():
    print('Indexer')
    chosen = None
    while chosen != '3' and chosen != '۳':
        chosen = input('Choose:\n\t'
                       '1) Build the index\n\t'
                       '2) Delete the index\n\t'
                       '3) Back\n')
        if chosen == '1' or chosen == '۱':
            directory = input('JSONs directory? (default to ./content/) ')
            es_connection = input('Elasticsearch connection? (default to localhost:9200) ')
            params = dict()
            if directory:
                params['directory'] = directory
            if es_connection:
                params['es_connection'] = {
                    'host': es_connection.split(':')[0],
                    'port': int(es_connection.split(':')[1]),
                }
            indexer.index(**params)  # TODO AuthorizationException, I think it's gone
            print('Done.')
        elif chosen == '2' or chosen == '۲':
            es_connection = input('Elasticsearch connection? (default to localhost:9200) ')
            if es_connection:
                indexer.delete_index(es_connection={
                    'host': es_connection.split(':')[0],
                    'port': int(es_connection.split(':')[1]),
                })
            else:
                indexer.delete_index()
            print('Done.')


def ui_pageRanker():
    print('PageRanker')
    es_connection = input('Elasticsearch connection? (default to localhost:9200) ')
    params = dict()
    if es_connection:
        params['es_connection'] = {
        'host': es_connection.split(':')[0],
        'port': int(es_connection.split(':')[1]),
        }
        pageranker.pagerank(**params)
        print('Done.')



def ui_searcher():
    print('Searcher') # HERE!!!
    es_connection = input('Elasticsearch connection? (default to localhost:9200) ')
    params = dict()
    if es_connection:
        params['es_connection'] = {
        'host': es_connection.split(':')[0],
        'port': int(es_connection.split(':')[1]),
        }
        searcher.search(**params)
        print('Done.')


def ui_main():
    chosen = None
    while chosen != '5' and chosen != '۵':
        chosen = input('Choose:\n\t'
                       '1) Crawler\n\t'
                       '2) Indexer\n\t'
                       '3) PageRanker\n\t'
                       '4) Searcher\n\t'
                       '5) Exit\n')
        if chosen == '1' or chosen == '۱':
            ui_crawler()
        elif chosen == '2' or chosen == '۲':
            ui_indexer()
        elif chosen == '3' or chosen == '۳':
            ui_pageRanker()
        elif chosen == '4' or chosen == '۳': # insert persian 4
            ui_searcher()


if __name__ == '__main__':
    ui_main()
