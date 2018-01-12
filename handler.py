from subprocess import call

import crawler

start_urls = [
    # 'http://viraz.blog.ir/',
    'http://shayanh.blog.ir/',
    'http://avocado.blog.ir/',
    'http://sirnarenji.blog.ir/',
    # 'http://arameeesh.blog.ir/'
]
start_urls = ','.join(start_urls)
in_degree = 5
n = 8
command = 'scrapy crawl blogs -a start_urls=%s' % start_urls
if in_degree:
    command += ' -a in_degree=%d' % in_degree
if n:
    command += ' -a n=%d' % n
call(command, shell=True, cwd='crawler')  # We run crawler this way because calling crawler API wouldn't load settings
# crawler.run(start_urls, in_degree, n)  # For debugging purposes
