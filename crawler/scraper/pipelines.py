import json
import os
import shutil

from scrapy.exceptions import DropItem


class CheckerPipeline(object):
    def __init__(self):
        self.seen_blogs = set()
        self.ignored_blogs = set()

    def process_item(self, item, spider):
        blog_name = item['blog_url'].split('.blog.ir')[0].split('/')[-1]
        if item['type'] == 'blog':
            if len(self.seen_blogs) == spider.n:
                # posts remaining in the queue are not processed by using the line below, so this isn't good
                # spider.crawler.engine.close_spider(spider)
                spider.continue_crawling_blogs = False
                self.ignored_blogs.add(blog_name)
                raise DropItem(
                    '(%s) It is enough for blogs themselves, now we only continue creating queued posts and then exit' %
                    item['blog_url'])
            elif blog_name in self.seen_blogs:
                raise DropItem('Duplicate url found: %s' % item['blog_url'])
            else:
                self.seen_blogs.add(blog_name)
        else:  # item['type'] == 'post'
            if blog_name in self.ignored_blogs:
                raise DropItem("This post's blog was ignored, so it will be ignored. Blog: %s" % blog_name)
        return item


class JsonWriterPipeline(object):
    ROOT_FOLDER = '../result'

    def __init__(self):
        self.num = 0

    def open_spider(self, spider):
        shutil.rmtree(self.ROOT_FOLDER, ignore_errors=True, onerror=None)
        os.mkdir(self.ROOT_FOLDER)

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        filepath = '%s/%d.json' % (self.ROOT_FOLDER, self.num)
        with open(filepath, 'w') as file:
            file.write(json.dumps(dict(item), ensure_ascii=False))
        self.num += 1
        return item
