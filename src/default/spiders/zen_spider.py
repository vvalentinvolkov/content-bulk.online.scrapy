from datetime import date

import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..items import CommonArticleItem


class ZenSpider(scrapy.Spider):

    name = 'ZenSpider'
    allowed_domains = ['zen.yandex.ru']

    ZEN_MAIN = 'https://zen.yandex.ru/'

    CSS_SELECTORS = {
        'a_articles_from_main': '.feed__row._items-count_1 .card-image-one-column-view__content>a',
        'btn_likes': 'button[aria-label="Like"], button[aria-label="Нравится"]',
        'span_likes': '.left-column-button__text.left-column-button__text_can-be-compact.left-column-button__text_short'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.ZEN_MAIN, callback=self.parse_main, dont_filter=True)

    def parse_main(self, response):
        """Ищет на главной странице ссылки на статьи,
        игнорируя видео и ссылки на стороние сайты (см. self.allowed_domains) """
        link_articles_from_main = (a.attrib['href'] for a in response.css(self.CSS_SELECTORS['a_articles_from_main']))

        # for link in link_articles_from_main:
        for link in ['https://zen.yandex.ru/media/holmogorow/kod-onegina-o-chem-na-samom-dele-roman-v-stihah-pushkina-616bdee2c67cad14546ba729']:
            yield SeleniumRequest(url=link,
                                  callback=self.parse,
                                  wait_time=3,
                                  wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, '.left-column-button__text_short'))
                                  )

    def parse(self, response, **kwargs):
        """Ищет инфу на странице статьи"""
        l = ItemLoader(item=CommonArticleItem(), response=response)

        l.add_value('source', 'zen')
        l.add_css('title', 'h1::text')
        l.add_value('link', response.url)

        l.add_value('parsing_date', date.today())
        l.add_css('public_date', '.article-stats-view__item[itemprop="datePublished"]::text')

        l.add_css('likes', '.left-block-redesign-view button:nth-child(1) .left-column-button__text_short::text')
        l.add_css('comments', '.left-block-redesign-view button:nth-child(3) .left-column-button__text_short::text')
        l.add_css('visitors', '.article-stats-view__tip div:nth-child(1) span::text')
        l.add_css('reads', '.article-stats-view__tip div:nth-child(2) span::text')
        l.add_css('read_time', '.article-stats-view__tip div:nth-child(3) span::text')
        l.add_css('subscribers', '.publisher-controls__subtitle::text')

        # l.add_css('length', '.article-render[itemprop = "articleBody"] span::text')
        # l.add_css('num_images', '.article-render[itemprop = "articleBody"] img')
        print(l.load_item())
