from datetime import date

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..items import CommonArticleItem
from ..loaders import ZenLoader


class ZenSpider(scrapy.Spider):
    """Spider для статей из ЯндексДзена"""

    name = 'ZenSpider'
    allowed_domains = ['zen.yandex.ru']
    start_urls = ['https://zen.yandex.ru/']

    LIMIT_PARSED_ARTICLES_NUM = 3
    parsed_articles = 0

    def parse(self, response, **kwargs):
        """Ищет на главной странице ссылки на статьи,
        игнорируя видео и ссылки на стороние сайты (см. self.allowed_domains) """
        link_articles_from_main = (a.attrib['href'] for a in
                                   response.css('.feed__row._items-count_1 .card-image-one-column-view__content > a'))

        for link in link_articles_from_main:
            yield SeleniumRequest(url=link,
                                  callback=self.parse_article,
                                  wait_time=3,
                                  wait_until=EC.element_to_be_clickable(
                                      (By.CSS_SELECTOR, '.left-column-button__text_short'))
                                  )
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True)

    def parse_article(self, response, **kwargs):
        """Ищет инфу на странице статьи и передает значение из параметра "selector" в виде <Selector> -
        может передавать и список <Selector>"""
        zen_loader = ZenLoader(item=CommonArticleItem(), selector=response.css('body'))

        zen_loader.add_str_value('source', 'zen')
        zen_loader.add_css('title', 'h1::text')
        # zen_loader.add_value('link', response.url)
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

        print(zen_loader.load_item())
        if self.parsed_articles >= self.LIMIT_PARSED_ARTICLES_NUM:
            raise CloseSpider
        else:
            self.parsed_articles += 1
