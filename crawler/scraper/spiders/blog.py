import re
import scrapy
from bs4 import BeautifulSoup


class BlogSpider(scrapy.Spider):
    name = 'blogs'
    allowed_domains = ['blog.ir']
    custom_settings = dict()

    def add_rss_to_url(self, url):
        if url[-1] == '/':
            url = url[:-1]
        return '%s/rss/' % url

    def __init__(self, start_urls='', in_degree=5, n=1000):
        super().__init__()
        self.start_urls = [self.add_rss_to_url(url) for url in start_urls.split(',')]
        self.in_degree = int(in_degree)
        self.n = int(n)
        self.custom_settings['CLOSESPIDER_ITEMCOUNT'] = n

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'xml')
        data = {
            'type': 'blog',
            'blog_name': soup.find('title').string,
            'blog_url': soup.find('link').string
        }
        if 'shade' in soup.find('link').string:
            print('a')
        post_urls = list()
        for i, post in enumerate(soup.find_all('item')[:5]):
            post_urls.append(post.find('link').string)
            data['post_url_%d' % (i+1)] = post.find('link').string
            data['post_title_%d' % (i+1)] = post.find('title').string
            data['post_content_%d' % (i+1)] = BeautifulSoup(post.find('description').string, 'html.parser').get_text()
        yield data

        for url in post_urls:
            yield response.follow(url, callback=self.parse_post)

    def parse_post(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        # post_content = soup.find(class_='post').find(class_='body').find_all('div', class_='cnt')[0].get_text().strip()  # TODO Emtiazi
        comment_urls = list()
        for comment in soup.find_all(class_='post_comments'):
            url = comment.find('a', class_='website')['href'] if comment.find('a', class_='website') else None
            if url and re.search('.+\.blog.ir', url):
                comment_urls.append(url)
        yield {
            'type': 'post',
            'blog_url': '%s.blog.ir' % response.url.split('.blog.ir')[0],
            'post_url': response.url,
            'comment_urls': comment_urls
        }

        for url in comment_urls:
            yield response.follow(self.add_rss_to_url(url), callback=self.parse)
