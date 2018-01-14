import json
import os
import shutil

from scrapy.exceptions import DropItem


class CheckerPipeline(object):
    def __init__(self):
        self.blogs_seen = set()

    def process_item(self, item, spider):
        if item['type'] == 'blog':
            if len(self.blogs_seen) == spider.n:
                # posts remaining in the queue are not processed by using the line below, so this isn't good
                # spider.crawler.engine.close_spider(spider)
                spider.continue_crawling_blogs = False
                raise DropItem(
                    '(%s) It is enough for blogs themselves, now we only continue creating queued posts and then exit' %
                    item['blog_url'])
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
            post_num = item['post_num']
            item_name = item['blog_url'].split('.blog.ir')[0].split('/')[-1] + ' (%d)' % post_num
            del item['post_num']
        filepath = '%s/%s/%s.json' % (self.ROOT_FOLDER, item_type, item_name)
        with open(filepath, 'w') as file:
            file.write(json.dumps(dict(item), ensure_ascii=False))
        return item
