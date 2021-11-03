from collections import OrderedDict
from datetime import date

import pymongo
import scrapy
from pymongo.errors import ConnectionFailure
from scrapy.exceptions import CloseSpider
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..items import ZenArticle
from ..loaders import ZenLoader


class ZenSpider(scrapy.Spider):
    """Spider для статей из ЯндексДзена"""

    name = 'ZenSpider'
    allowed_domains = ['zen.yandex.ru']
    start_urls = ['https://zen.yandex.ru/']

    LIMIT_PARSED_ARTICLES_NUM = 2
    parsed_articles = 0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        mongo_url = crawler.settings.get('MONGO_URL')
        mongo_db = crawler.settings.get('MONGO_DB_NAME')
        col_name = crawler.settings.get('MONGO_COLLECTION_NAME')
        return ZenSpider(mongo_url=mongo_url, mongo_db=mongo_db, col_name=col_name,)


    def parse(self, response, **kwargs):
        """Ищет на главной странице ссылки на статьи,
        игнорируя видео и ссылки на стороние сайты (см. self.allowed_domains) """
        link_articles_from_main = (a.attrib['href'] for a in
                                   response.css('.feed__row._items-count_1 .card-image-one-column-view__content > a'))

        # for link in link_articles_from_main:
        for link in ['https://zen.yandex.ru/media/automaniac/razobral-dvigatel-lady-vesty-18-l-vaz-21179-pokazyvaiu-iz-chego-sdelan-etot-motor-i-est-li-v-nem-rossiiskie-komplektuiuscie-61519246bd215b71fd3c6b26',
                     'https://zen.yandex.ru/media/zenwhatsnew/klast-ili-lojit-proidite-korotkii-test-na-gramotnost-i-uznaite-chto-u-vas-po-russkomu-iazyku-na-samom-dele-61370e227ce5df2042c41fe1',
                     'https://zen.yandex.ru/media/automaniac/razobral-dvigatel-lady-vesty-18-l-vaz-21179-pokazyvaiu-iz-chego-sdelan-etot-motor-i-est-li-v-nem-rossiiskie-komplektuiuscie-61519246bd215b71fd3c6b26']:
            yield SeleniumRequest(url=link,
                                  callback=self.parse_article,
                                  wait_time=3,
                                  wait_until=EC.element_to_be_clickable(
                                      (By.CSS_SELECTOR, '.left-column-button__text_short')),
                                  flags=['dup_middleware']
                                  )
        # yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse_article(self, response, **kwargs):
        """Ищет инфу на странице статьи и передает значение из параметра "selector" в виде <Selector> -
        может передавать и список <Selector>"""
        zen_loader = ZenLoader(item=ZenArticle(), selector=response.css('body'))

        zen_loader.add_str_value('source', 'zen')
        zen_loader.add_css('title', 'h1::text')
        zen_loader.add_value('url', response.url)
        #
        # zen_loader.add_value('parsing_date', date.today())
        # zen_loader.add_css('public_date', '.article-stats-view__item[itemprop="datePublished"]::text')
        #
        # zen_loader.add_css('likes', '.left-block-redesign-view button:nth-child(1) .left-column-button__text_short::text')
        # zen_loader.add_css('comments', '.left-block-redesign-view button:nth-child(3) .left-column-button__text_short::text')
        # zen_loader.add_css('visitors', '.article-stats-view__tip div:nth-child(1) span::text')
        # zen_loader.add_css('reads', '.article-stats-view__tip div:nth-child(2) span::text')
        # zen_loader.add_css('read_time', '.article-stats-view__tip div:nth-child(3) span::text')
        # zen_loader.add_css('subscribers', '.publisher-controls__subtitle::text')

        # zen_loader.add_css('length', '.article-render[itemprop = "articleBody"] span::text')
        # zen_loader.add_css('num_images', '.article-render[itemprop = "articleBody"] img')

        item = zen_loader.load_item()
        if self.parsed_articles >= self.LIMIT_PARSED_ARTICLES_NUM:
            raise CloseSpider
        else:
            self.parsed_articles += 1
            return item
