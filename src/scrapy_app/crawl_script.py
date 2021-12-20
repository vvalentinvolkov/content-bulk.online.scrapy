import sys
import os

from scrapy.settings import Settings

from .spiders.zen_spider import ZenSpider

sys.path.insert(0, os.path.abspath('..'))

from multiprocessing import Process

from scrapy.crawler import CrawlerProcess, Crawler
from . import settings as module_settings

SPIDERS = {
    'ZenSpider': ZenSpider
}


class CrawlScript:

    def __init__(self):
        self.process = CrawlerProcess(Settings())
        self.process.settings.setmodule(module_settings)

    def _crawl(self, spider: str, settings: dict):
        self.process.settings.update(settings)
        self.process.crawl(SPIDERS[spider])
        print(f'Start crawl {spider}')
        self.process.start()

    def crawl(self, spider: str, settings: dict):
        # p = Process(target=self._crawl, args=(spider, settings))
        # p.start()
        # p.join()
        self._crawl(spider, settings)
        print('Stop crawl')
