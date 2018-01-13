from subprocess import call

import crawler
import indexer


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
            indexer.index()  # TODO AuthorizationException occurs seldom
            print('Done.')
        elif chosen == '2' or chosen == '۲':
            indexer.delete_index()
            print('Done.')


def ui_main():
    chosen = None
    while chosen != '5' and chosen != '۵':
        chosen = input('Choose:\n\t'
                       '1) Crawler\n\t'
                       '2) Indexer\n\t'
                       '3) TBD\n\t'
                       '4) TBD\n\t'
                       '5) Exit\n')
        if chosen == '1' or chosen == '۱':
            ui_crawler()
        elif chosen == '2' or chosen == '۲':
            ui_indexer()


if __name__ == '__main__':
    ui_main()
