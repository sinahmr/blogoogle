import logging
import re
import urllib

import scrapy
from bs4 import BeautifulSoup


class BlogSpider(scrapy.Spider):
    name = 'blogs'
    allowed_domains = ['blog.ir']
    continue_crawling_blogs = True

    def add_rss_to_url(self, url):
        if url[-1] == '/':
            url = url[:-1]
        return '%s/rss/' % url

    def __init__(self, start_urls='', in_degree=5, n=1000):
        super().__init__()
        self.start_urls = [self.add_rss_to_url(url) for url in start_urls.split(',')]
        self.in_degree = int(in_degree)
        self.n = int(n)
        # logging.getLogger('scrapy').setLevel(logging.WARNING)

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'xml')
        data = {
            'type': 'blog',
            'blog_name': soup.find('title').string or '',
            'blog_url': soup.find('link').string or ''
        }
        post_urls = list()
        for i, post in enumerate(soup.find_all('item')[:5]):
            post_urls.append(post.find('link').string)
            data['post_url_%d' % (i+1)] = urllib.parse.unquote(post.find('link').string or '')
            data['post_title_%d' % (i+1)] = post.find('title').string or ''
            data['post_content_%d' % (i+1)] = BeautifulSoup(post.find('description').string or '', 'html.parser')\
                .get_text()
        yield data

        for i, url in enumerate(post_urls):
            yield response.follow(url, callback=self.parse_post, meta={'post_num': i+1})

    def parse_post(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        try:
            post_container = soup.find('div', class_='post') or soup.find('div', id='block-post')
            post_full_content = post_container.find('div', {'class': ['body', 'post-matn', 'post-content', 'main-post',
                                                                      'postbody', 'post-con', 'context', 'post-body']})\
                .get_text().strip()
        except AttributeError:
            post_full_content = ''
        comment_urls = list()
        for comment in soup.find_all(class_='post_comments'):
            url = comment.find('a', class_='website')['href'] if comment.find('a', class_='website') else None
            if url and re.search('.+\.blog.ir', url):
                if url not in comment_urls:
                    comment_urls.append(response.urljoin(url))
        yield {
            'type': 'post',
            'blog_url': '%s.blog.ir' % response.url.split('.blog.ir')[0],
            'post_url': urllib.parse.unquote(response.url),
            'comment_urls': comment_urls,
            'post_full_content': post_full_content,
            # 'post_num': response.meta['post_num']
        }

        if self.continue_crawling_blogs:
            for url in comment_urls[:self.in_degree]:
                yield response.follow(self.add_rss_to_url(url), callback=self.parse)
