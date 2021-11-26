import scrapy
from scrapy.crawler import CrawlerProcess

from src.default.spiders.zen_spider import ZenSpider

process = CrawlerProcess()

process.crawl(ZenSpider)
process.start()     # the script will block here until the crawling is finished