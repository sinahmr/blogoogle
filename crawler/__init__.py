from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from crawler.scraper.spiders.blog import BlogSpider


def run(*args):  # This method can be used for debugging
    settings = get_project_settings()
    # os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawler.crawler.settings'
    # settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
    # settings.setmodule(settings_module_path, priority='project')
    # settings.set('FEED_FORMAT', 'json')
    # settings.set('FEED_URI', 'result.json')
    configure_logging()

    process = CrawlerProcess(settings)
    process.crawl(BlogSpider, *args)
    process.start()  # The script will block here until the crawling is finished
