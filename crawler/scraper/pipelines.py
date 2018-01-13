# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import shutil

from scrapy.exceptions import DropItem


class DuplicatesPipeline(object):

    def __init__(self):
        self.blogs_seen = set()

    def process_item(self, item, spider):
        if item['type'] == 'blog':
            if len(self.blogs_seen) == spider.n:
                spider.crawler.engine.close_spider(spider)  # TODO posts remaining in the queue are not processed :|
                raise DropItem('(%s) It is enough for blogs themselves, \
                                now we only continue creating queued posts and then exit' % item['blog_url'])
            elif item['blog_url'] in self.blogs_seen:
                raise DropItem('Duplicate url found: %s' % item['blog_url'])
            else:
                self.blogs_seen.add(item['blog_url'])
        return item


class JsonWriterPipeline(object):
    ROOT_FOLDER = '../content'

    def open_spider(self, spider):
        shutil.rmtree(self.ROOT_FOLDER, ignore_errors=True, onerror=None)
        os.mkdir(self.ROOT_FOLDER)
        os.mkdir('%s/blog' % self.ROOT_FOLDER)
        os.mkdir('%s/post' % self.ROOT_FOLDER)

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        item_type = item['type']
        if item_type == 'blog':
            item_name = item['blog_url'].split('.blog.ir')[0].split('/')[-1]
        else:
            item_name = item['blog_url'].split('.blog.ir')[0].split('/')[-1] + ' (%s)' % item['post_url'].split('/')[-1]
        filepath = '%s/%s/%s.json' % (self.ROOT_FOLDER, item_type, item_name)
        with open(filepath, 'w') as file:
            file.write(json.dumps(dict(item), ensure_ascii=False))
        return item
